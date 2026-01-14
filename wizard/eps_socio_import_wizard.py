# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import base64
import csv
import io
import logging

_logger = logging.getLogger(__name__)

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    _logger.warning('openpyxl no está instalado. La importación de archivos XLSX no estará disponible.')


class EpsSocioImportWizard(models.TransientModel):
    _name = 'eps.socio.import.wizard'
    _description = 'Asistente de importación de socios'

    file = fields.Binary(string='Archivo', required=True, help='Archivo CSV o XLSX con los datos de los socios')
    filename = fields.Char(string='Nombre del archivo')
    caja_id = fields.Many2one('eps.caja', string='Caja', required=True, help='Caja a la que pertenecerán los socios importados')
    delimiter = fields.Selection([
        (',', 'Coma (,)'),
        (';', 'Punto y coma (;)'),
        ('\t', 'Tabulador'),
    ], string='Delimitador CSV', default=',', help='Solo aplica para archivos CSV')
    update_existing = fields.Boolean(string='Actualizar existentes', default=False, 
                                     help='Si está marcado, actualiza socios existentes por cédula. Si no, los omite.')
    
    import_result = fields.Text(string='Resultado', readonly=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Completado'),
    ], default='draft')

    def action_import(self):
        """Procesa el archivo y crea/actualiza los socios"""
        self.ensure_one()
        
        if not self.file:
            raise UserError(_('Debe seleccionar un archivo.'))
        
        # Decodificar el archivo
        file_content = base64.b64decode(self.file)
        
        # Determinar el tipo de archivo
        if self.filename and self.filename.endswith('.xlsx'):
            if not OPENPYXL_AVAILABLE:
                raise UserError(_('No se puede procesar archivos XLSX. Instale openpyxl: pip3 install openpyxl'))
            result = self._import_xlsx(file_content)
        elif self.filename and (self.filename.endswith('.csv') or self.filename.endswith('.txt')):
            result = self._import_csv(file_content)
        else:
            raise UserError(_('Formato de archivo no soportado. Use CSV o XLSX.'))
        
        self.write({
            'import_result': result,
            'state': 'done',
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'eps.socio.import.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _import_csv(self, file_content):
        """Importa desde archivo CSV"""
        try:
            # Intentar decodificar con diferentes encodings
            for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                try:
                    content_str = file_content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise UserError(_('No se pudo decodificar el archivo. Verifique el formato.'))
            
            csv_reader = csv.DictReader(io.StringIO(content_str), delimiter=self.delimiter)
            return self._process_rows(csv_reader)
            
        except Exception as e:
            raise UserError(_('Error al leer el archivo CSV: %s') % str(e))

    def _import_xlsx(self, file_content):
        """Importa desde archivo XLSX"""
        try:
            workbook = openpyxl.load_workbook(io.BytesIO(file_content))
            sheet = workbook.active
            
            # Obtener headers de la primera fila
            headers = [cell.value for cell in sheet[1]]
            
            # Crear lista de diccionarios
            rows = []
            for row in sheet.iter_rows(min_row=2, values_only=True):
                row_dict = {headers[i]: row[i] for i in range(len(headers)) if i < len(row)}
                rows.append(row_dict)
            
            return self._process_rows(rows)
            
        except Exception as e:
            raise UserError(_('Error al leer el archivo XLSX: %s') % str(e))

    def _process_rows(self, rows):
        """Procesa las filas y crea/actualiza socios"""
        created = 0
        updated = 0
        skipped = 0
        errors = []
        
        for idx, row in enumerate(rows, start=2):
            try:
                # Saltar filas vacías
                if not row or not any(row.values()):
                    continue
                
                # Extraer datos (soportar diferentes nombres de columnas)
                cedula = self._get_value(row, ['cedula', 'Cedula', 'CEDULA', 'CI', 'ci'])
                if not cedula:
                    skipped += 1
                    errors.append(f"Fila {idx}: Cédula vacía - omitida")
                    continue
                
                # Preparar valores
                values = self._prepare_values(row)
                values['caja_id'] = self.caja_id.id
                
                # Buscar si existe
                existing = self.env['eps.socio'].search([
                    ('cedula', '=', str(cedula)),
                    ('caja_id', '=', self.caja_id.id)
                ], limit=1)
                
                if existing:
                    if self.update_existing:
                        existing.write(values)
                        updated += 1
                    else:
                        skipped += 1
                        errors.append(f"Fila {idx}: Socio con cédula {cedula} ya existe - omitido")
                else:
                    self.env['eps.socio'].create(values)
                    created += 1
                    
            except Exception as e:
                skipped += 1
                errors.append(f"Fila {idx}: {str(e)}")
        
        # Construir resultado
        result = f"""
IMPORTACIÓN COMPLETADA

Registros creados: {created}
Registros actualizados: {updated}
Registros omitidos: {skipped}

"""
        if errors:
            result += "\nERRORES Y ADVERTENCIAS:\n"
            result += "\n".join(errors[:50])  # Limitar a 50 errores
            if len(errors) > 50:
                result += f"\n... y {len(errors) - 50} errores más"
        
        return result

    def _get_value(self, row, possible_keys):
        """Obtiene valor de un diccionario probando múltiples keys"""
        for key in possible_keys:
            if key in row and row[key]:
                return row[key]
        return None

    def _prepare_values(self, row):
        """Prepara los valores para crear/actualizar un socio"""
        values = {}
        
        # Campos de texto
        text_mappings = {
            'cedula': ['cedula', 'Cedula', 'CEDULA', 'CI', 'ci'],
            'name': ['nombre', 'Nombre', 'NOMBRE', 'nombres', 'Nombres', 'name'],
            'apellido': ['apellido', 'Apellido', 'APELLIDO', 'apellidos', 'Apellidos'],
            'telefono': ['telefono', 'Telefono', 'TELEFONO', 'tel', 'Tel', 'celular', 'Celular'],
            'email': ['email', 'Email', 'EMAIL', 'correo', 'Correo', 'mail'],
            'direccion': ['direccion', 'Direccion', 'DIRECCION', 'domicilio', 'Domicilio'],
            'observaciones': ['observaciones', 'Observaciones', 'OBSERVACIONES', 'notas', 'Notas'],
        }
        
        for field, keys in text_mappings.items():
            value = self._get_value(row, keys)
            if value:
                values[field] = str(value).strip()
        
        # Género
        genero = self._get_value(row, ['genero', 'Genero', 'GENERO', 'sexo', 'Sexo'])
        if genero:
            genero_str = str(genero).strip().lower()
            if genero_str in ['m', 'mujer', 'femenino', 'f']:
                values['genero'] = 'mujer'
            elif genero_str in ['h', 'hombre', 'masculino', 'm']:
                values['genero'] = 'hombre'
        
        # Fechas
        fecha_ingreso = self._get_value(row, ['fecha_ingreso', 'Fecha Ingreso', 'FECHA_INGRESO', 'ingreso'])
        if fecha_ingreso:
            values['fecha_ingreso'] = self._parse_date(fecha_ingreso)
        
        fecha_nacimiento = self._get_value(row, ['fecha_nacimiento', 'Fecha Nacimiento', 'FECHA_NACIMIENTO', 'nacimiento'])
        if fecha_nacimiento:
            values['fecha_nacimiento'] = self._parse_date(fecha_nacimiento)
        
        # Campos booleanos
        bool_mappings = {
            'es_cabeza_hogar': ['cabeza_hogar', 'Cabeza Hogar', 'CABEZA_HOGAR', 'cabeza_familia', 'es_cabeza_hogar'],
            'tiene_discapacidad': ['tiene_discapacidad', 'Discapacidad', 'DISCAPACIDAD', 'discapacidad'],
            'es_indigena': ['es_indigena', 'Indigena', 'INDIGENA', 'indigena'],
            'es_afroecuatoriano': ['es_afroecuatoriano', 'Afroecuatoriano', 'AFROECUATORIANO', 'afro'],
            'es_montubio': ['es_montubio', 'Montubio', 'MONTUBIO', 'montubio'],
            'es_mestizo': ['es_mestizo', 'Mestizo', 'MESTIZO', 'mestizo'],
            'active': ['activo', 'Activo', 'ACTIVO', 'active', 'Active'],
        }
        
        for field, keys in bool_mappings.items():
            value = self._get_value(row, keys)
            if value is not None:
                values[field] = self._parse_boolean(value)
        
        # Campos numéricos
        porcentaje_disc = self._get_value(row, ['porcentaje_discapacidad', 'Porcentaje Discapacidad', '%_DISCAPACIDAD'])
        if porcentaje_disc:
            try:
                # Convertir a entero y luego a string para el selection
                porcentaje = int(float(porcentaje_disc))
                # Redondear al múltiplo de 10 más cercano
                porcentaje = round(porcentaje / 10) * 10
                if 10 <= porcentaje <= 100:
                    values['porcentaje_discapacidad'] = str(porcentaje)
            except:
                pass
        
        num_dependientes = self._get_value(row, ['num_dependientes', 'Dependientes', 'DEPENDIENTES', 'dependientes'])
        if num_dependientes:
            try:
                values['num_dependientes'] = int(num_dependientes)
            except:
                pass
        
        # Estado civil
        estado_civil = self._get_value(row, ['estado_civil', 'Estado Civil', 'ESTADO_CIVIL'])
        if estado_civil:
            estado_str = str(estado_civil).strip().lower()
            valid_states = ['soltero', 'casado', 'divorciado', 'viudo', 'union_libre']
            for state in valid_states:
                if state in estado_str or estado_str in state:
                    values['estado_civil'] = state
                    break
        
        return values

    def _parse_date(self, date_value):
        """Convierte diferentes formatos de fecha a formato Odoo (YYYY-MM-DD)"""
        if not date_value:
            return None
        
        # Si ya es una fecha, convertir a string
        if hasattr(date_value, 'strftime'):
            return date_value.strftime('%Y-%m-%d')
        
        date_str = str(date_value).strip()
        
        # Intentar diferentes formatos
        import datetime
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d', '%d.%m.%Y']
        
        for fmt in formats:
            try:
                date_obj = datetime.datetime.strptime(date_str, fmt)
                return date_obj.strftime('%Y-%m-%d')
            except:
                continue
        
        return None

    def _parse_boolean(self, value):
        """Convierte diferentes valores a booleano"""
        if isinstance(value, bool):
            return value
        
        if value is None:
            return False
        
        str_value = str(value).strip().lower()
        return str_value in ['1', 'true', 'verdadero', 'sí', 'si', 'yes', 'x', 's']

    def action_close(self):
        """Cierra el wizard y vuelve a la vista de socios"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'eps.socio',
            'view_mode': 'list,form',
            'domain': [('caja_id', '=', self.caja_id.id)],
        }

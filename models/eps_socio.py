# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date


class EpsSocio(models.Model):
    _name = 'eps.socio'
    _description = 'Socio de Caja de Ahorro EPS'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_ingreso desc, name'

    # === IDENTIFICACIÓN ===
    name = fields.Char(
        string='Nombres',
        required=True,
        tracking=True,
        help="Nombres del socio"
    )
    
    apellido = fields.Char(
        string='Apellidos',
        tracking=True,
        help="Apellidos del socio"
    )
    
    nombre_completo = fields.Char(
        string='Nombre Completo',
        compute='_compute_nombre_completo',
        store=True,
        help="Nombre y apellido concatenados"
    )
    
    cedula = fields.Char(
        string='Cédula',
        required=True,
        tracking=True,
        help="Número de cédula de identidad (único por caja)"
    )
    
    # === RELACIÓN CON CAJA ===
    caja_id = fields.Many2one(
        'eps.caja',
        string='Caja de Ahorro',
        required=True,
        ondelete='restrict',
        tracking=True
    )
    
    # === FECHAS ===
    fecha_ingreso = fields.Date(
        string='Fecha de Ingreso',
        required=True,
        default=fields.Date.today,
        tracking=True,
        help="Fecha en que el socio ingresó a la caja"
    )
    
    fecha_nacimiento = fields.Date(
        string='Fecha de Nacimiento',
        tracking=True
    )
    
    edad = fields.Integer(
        string='Edad',
        compute='_compute_edad',
        store=True,
        help="Edad calculada automáticamente"
    )
    
    # === CONTACTO ===
    telefono = fields.Char(
        string='Teléfono',
        tracking=True
    )
    
    email = fields.Char(
        string='Correo Electrónico',
        tracking=True
    )
    
    direccion = fields.Text(
        string='Dirección'
    )
    
    # === INDICADORES SOCIALES ===
    genero = fields.Selection([
        ('mujer', 'Mujer'),
        ('hombre', 'Hombre'),
        ('otro', 'Otro')
    ], string='Género', required=True, default='mujer', tracking=True)
    
    es_tercera_edad = fields.Boolean(
        string='Tercera Edad',
        compute='_compute_tercera_edad',
        store=True,
        help="Mayor o igual a 65 años"
    )
    
    tercera_edad_texto = fields.Char(
        string='3ra Edad',
        compute='_compute_textos_booleanos'
    )
    
    es_menor_edad = fields.Boolean(
        string='Menor de Edad',
        compute='_compute_menor_edad',
        store=True,
        help="Menor de 18 años"
    )
    
    menor_edad_texto = fields.Char(
        string='Menor',
        compute='_compute_textos_booleanos'
    )
    
    tiene_discapacidad = fields.Boolean(
        string='Tiene Discapacidad',
        tracking=True
    )
    
    discapacidad_texto = fields.Char(
        string='Discapacidad',
        compute='_compute_textos_booleanos'
    )
    
    tipo_discapacidad = fields.Selection([
        ('fisica', 'Física'),
        ('visual', 'Visual'),
        ('auditiva', 'Auditiva'),
        ('intelectual', 'Intelectual'),
        ('psicosocial', 'Psicosocial'),
        ('multiple', 'Múltiple')
    ], string='Tipo de Discapacidad')
    
    porcentaje_discapacidad = fields.Selection([
        ('10', '10%'),
        ('20', '20%'),
        ('30', '30%'),
        ('40', '40%'),
        ('50', '50%'),
        ('60', '60%'),
        ('70', '70%'),
        ('80', '80%'),
        ('90', '90%'),
        ('100', '100%'),
    ], string='% Discapacidad', help="Porcentaje de discapacidad")
    
    es_cabeza_hogar = fields.Boolean(
        string='Cabeza de Hogar',
        tracking=True
    )
    
    cabeza_hogar_texto = fields.Char(
        string='Cabeza Hogar',
        compute='_compute_textos_booleanos'
    )
    
    num_dependientes = fields.Integer(
        string='Número de Dependientes',
        default=0
    )
    
    estado_civil = fields.Selection([
        ('soltero', 'Soltero/a'),
        ('casado', 'Casado/a'),
        ('divorciado', 'Divorciado/a'),
        ('viudo', 'Viudo/a'),
        ('union_libre', 'Unión Libre')
    ], string='Estado Civil', tracking=True)
    
    # === INDICADORES ÉTNICOS ===
    es_indigena = fields.Boolean(
        string='Indígena',
        tracking=True,
        help="Pertenece a pueblo o nacionalidad indígena"
    )
    
    es_afroecuatoriano = fields.Boolean(
        string='Afroecuatoriano/a',
        tracking=True
    )
    
    es_montubio = fields.Boolean(
        string='Montubio/a',
        tracking=True
    )
    
    es_mestizo = fields.Boolean(
        string='Mestizo/a',
        tracking=True
    )
    
    # === REPRESENTANTE LEGAL (para menores de edad) ===
    representante_nombre = fields.Char(
        string='Nombre del Representante',
        help="Nombre completo del padre, madre o tutor legal"
    )
    
    representante_cedula = fields.Char(
        string='Cédula del Representante'
    )
    
    representante_relacion = fields.Selection([
        ('padre', 'Padre'),
        ('madre', 'Madre'),
        ('tutor', 'Tutor Legal'),
        ('otro', 'Otro')
    ], string='Relación con el Representante')
    
    # === ESTADO ===
    active = fields.Boolean(
        string='Activo',
        default=True,
        tracking=True,
        help="Desmarca para marcar al socio como inactivo (baja)"
    )
    
    estado = fields.Selection([
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('retirado', 'Retirado')
    ], string='Estado', default='activo', required=True, tracking=True)
    
    fecha_baja = fields.Date(
        string='Fecha de Baja',
        tracking=True,
        help="Fecha en que el socio se retiró de la caja"
    )
    
    motivo_baja = fields.Text(
        string='Motivo de Baja'
    )
    
    # === OBSERVACIONES ===
    observaciones = fields.Text(
        string='Observaciones'
    )
    
    # === RESTRICCIONES SQL ===
    _sql_constraints = [
        ('cedula_caja_unique',
         'UNIQUE(cedula, caja_id)',
         'Ya existe un socio con esta cédula en la caja seleccionada.')
    ]
    
    # === CAMPOS COMPUTADOS ===
    @api.depends('name', 'apellido')
    def _compute_nombre_completo(self):
        """Concatena nombre y apellido"""
        for socio in self:
            if socio.apellido:
                socio.nombre_completo = f"{socio.name} {socio.apellido}"
            else:
                socio.nombre_completo = socio.name or ''
    
    @api.depends('es_tercera_edad', 'es_menor_edad', 'tiene_discapacidad', 'es_cabeza_hogar')
    def _compute_textos_booleanos(self):
        """Convierte campos booleanos a texto Sí/No"""
        for socio in self:
            socio.tercera_edad_texto = 'Sí' if socio.es_tercera_edad else 'No'
            socio.menor_edad_texto = 'Sí' if socio.es_menor_edad else 'No'
            socio.discapacidad_texto = 'Sí' if socio.tiene_discapacidad else 'No'
            socio.cabeza_hogar_texto = 'Sí' if socio.es_cabeza_hogar else 'No'
    
    @api.depends('fecha_nacimiento')
    def _compute_edad(self):
        """Calcula la edad del socio basándose en la fecha de nacimiento"""
        for socio in self:
            if socio.fecha_nacimiento:
                today = date.today()
                edad = today.year - socio.fecha_nacimiento.year
                # Ajustar si aún no ha cumplido años este año
                if (today.month, today.day) < (socio.fecha_nacimiento.month, socio.fecha_nacimiento.day):
                    edad -= 1
                socio.edad = edad
            else:
                socio.edad = 0
    
    @api.depends('edad')
    def _compute_tercera_edad(self):
        """Determina si el socio es de tercera edad (>= 65 años)"""
        for socio in self:
            socio.es_tercera_edad = socio.edad >= 65 if socio.edad else False
    
    @api.depends('edad')
    def _compute_menor_edad(self):
        """Determina si el socio es menor de edad (< 18 años)"""
        for socio in self:
            socio.es_menor_edad = socio.edad < 18 if socio.edad else False
    
    # === VALIDACIONES ===
    @api.onchange('telefono')
    def _onchange_telefono(self):
        """Valida que el teléfono tenga exactamente 10 dígitos"""
        if self.telefono:
            # Eliminar todo lo que no sea dígito
            telefono_limpio = ''.join(filter(str.isdigit, self.telefono))
            
            # Si el usuario escribió letras u otros caracteres, limpiar automáticamente
            if telefono_limpio != self.telefono.replace(' ', '').replace('-', ''):
                self.telefono = telefono_limpio
                return {
                    'warning': {
                        'title': 'Teléfono modificado',
                        'message': 'Se eliminaron caracteres no numéricos del teléfono.'
                    }
                }
            
            # Verificar longitud (10 dígitos para Ecuador)
            if len(telefono_limpio) != 10:
                return {
                    'warning': {
                        'title': 'Teléfono inválido',
                        'message': 'El teléfono debe tener exactamente 10 dígitos.'
                    }
                }
    
    @api.onchange('cedula')
    def _onchange_cedula(self):
        """Valida la cédula ecuatoriana en tiempo real"""
        if self.cedula:
            # Eliminar espacios y guiones
            cedula = self.cedula.replace(' ', '').replace('-', '')
            
            # Verificar que tenga solo dígitos
            if not cedula.isdigit():
                return {
                    'warning': {
                        'title': 'Cédula inválida',
                        'message': 'La cédula debe contener solo números.'
                    }
                }
            
            # Verificar longitud (10 dígitos para Ecuador)
            if len(cedula) != 10:
                return {
                    'warning': {
                        'title': 'Cédula inválida',
                        'message': 'La cédula debe tener exactamente 10 dígitos.'
                    }
                }
            
            # Validar provincia (primeros 2 dígitos)
            provincia = int(cedula[0:2])
            if provincia < 1 or provincia > 24:
                return {
                    'warning': {
                        'title': 'Cédula inválida',
                        'message': 'Los dos primeros dígitos no corresponden a una provincia válida (01-24).'
                    }
                }
            
            # Validar tercer dígito (debe ser menor a 6 para personas naturales)
            tercer_digito = int(cedula[2])
            if tercer_digito > 5:
                return {
                    'warning': {
                        'title': 'Cédula inválida',
                        'message': 'El tercer dígito debe ser menor a 6 para personas naturales.'
                    }
                }
            
            # Algoritmo de validación del dígito verificador
            coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
            suma = 0
            
            for i in range(9):
                valor = int(cedula[i]) * coeficientes[i]
                if valor >= 10:
                    valor -= 9
                suma += valor
            
            # Calcular dígito verificador
            resultado = suma % 10
            if resultado == 0:
                digito_verificador = 0
            else:
                digito_verificador = 10 - resultado
            
            # Comparar con el último dígito de la cédula
            if digito_verificador != int(cedula[9]):
                return {
                    'warning': {
                        'title': 'Cédula inválida',
                        'message': 'La cédula ingresada no es válida. Por favor verifique el número.'
                    }
                }
    
    @api.constrains('telefono')
    def _check_telefono(self):
        """Valida que el teléfono tenga exactamente 10 dígitos al guardar"""
        for socio in self:
            if socio.telefono:
                # Eliminar espacios y guiones
                telefono = socio.telefono.replace(' ', '').replace('-', '')
                
                # Verificar que tenga solo dígitos
                if not telefono.isdigit():
                    raise ValidationError(_('El teléfono debe contener solo números.'))
                
                # Verificar longitud
                if len(telefono) != 10:
                    raise ValidationError(_('El teléfono debe tener exactamente 10 dígitos.'))
    
    @api.constrains('cedula')
    def _check_cedula(self):
        """Valida que la cédula ecuatoriana sea correcta usando el algoritmo del dígito verificador"""
        for socio in self:
            if socio.cedula:
                # Eliminar espacios y guiones
                cedula = socio.cedula.replace(' ', '').replace('-', '')
                
                # Verificar que tenga solo dígitos
                if not cedula.isdigit():
                    raise ValidationError(_('La cédula debe contener solo números.'))
                
                # Verificar longitud (10 dígitos para Ecuador)
                if len(cedula) != 10:
                    raise ValidationError(_('La cédula debe tener exactamente 10 dígitos.'))
                
                # Validar provincia (primeros 2 dígitos)
                provincia = int(cedula[0:2])
                if provincia < 1 or provincia > 24:
                    raise ValidationError(_('Los dos primeros dígitos de la cédula no corresponden a una provincia válida (01-24).'))
                
                # Validar tercer dígito (debe ser menor a 6 para personas naturales)
                tercer_digito = int(cedula[2])
                if tercer_digito > 5:
                    raise ValidationError(_('El tercer dígito de la cédula debe ser menor a 6 para personas naturales.'))
                
                # Algoritmo de validación del dígito verificador
                coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
                suma = 0
                
                for i in range(9):
                    valor = int(cedula[i]) * coeficientes[i]
                    if valor >= 10:
                        valor -= 9
                    suma += valor
                
                # Calcular dígito verificador
                resultado = suma % 10
                if resultado == 0:
                    digito_verificador = 0
                else:
                    digito_verificador = 10 - resultado
                
                # Comparar con el último dígito de la cédula
                if digito_verificador != int(cedula[9]):
                    raise ValidationError(_('La cédula ingresada no es válida. Por favor verifique el número.'))
    
    @api.constrains('cedula')
    def _check_cedula_unique(self):
        """Valida que la cédula sea única en la caja"""
        for socio in self:
            if socio.cedula:
                cedula = socio.cedula.replace(' ', '').replace('-', '')
                # Buscar si ya existe otra persona con la misma cédula en esta caja
                existe = self.search([
                    ('cedula', '=', cedula),
                    ('caja_id', '=', socio.caja_id.id),
                    ('id', '!=', socio.id)
                ], limit=1)
                if existe:
                    raise ValidationError(_('Ya existe un socio con esta cédula en la caja seleccionada.'))
    
    @api.onchange('representante_cedula')
    def _onchange_representante_cedula(self):
        """Valida que la cédula del representante sea correcta"""
        for socio in self:
            if socio.representante_cedula:
                # Eliminar espacios y guiones
                cedula = socio.representante_cedula.replace(' ', '').replace('-', '')
                
                # Verificar que tenga solo dígitos
                if not cedula.isdigit():
                    raise ValidationError(_('La cédula del representante debe contener solo números.'))
                
                # Verificar longitud
                if len(cedula) != 10:
                    raise ValidationError(_('La cédula del representante debe tener exactamente 10 dígitos.'))
                
                # Validar provincia
                provincia = int(cedula[0:2])
                if provincia < 1 or provincia > 24:
                    raise ValidationError(_('La cédula del representante no es válida: provincia incorrecta.'))
                
                # Validar tercer dígito
                tercer_digito = int(cedula[2])
                if tercer_digito > 5:
                    raise ValidationError(_('La cédula del representante no es válida.'))
                
                # Algoritmo de validación
    @api.onchange('representante_cedula')
    def _onchange_representante_cedula(self):
        """Valida la cédula del representante en tiempo real"""
        if self.representante_cedula:
            # Eliminar espacios y guiones
            cedula = self.representante_cedula.replace(' ', '').replace('-', '')
            
            # Verificar que tenga solo dígitos
            if not cedula.isdigit():
                return {
                    'warning': {
                        'title': 'Cédula del representante inválida',
                        'message': 'La cédula debe contener solo números.'
                    }
                }
            
            # Verificar longitud
            if len(cedula) != 10:
                return {
                    'warning': {
                        'title': 'Cédula del representante inválida',
                        'message': 'La cédula debe tener exactamente 10 dígitos.'
                    }
                }
            
            # Validar provincia
            provincia = int(cedula[0:2])
            if provincia < 1 or provincia > 24:
                return {
                    'warning': {
                        'title': 'Cédula del representante inválida',
                        'message': 'Provincia incorrecta (debe estar entre 01-24).'
                    }
                }
            
            # Validar tercer dígito
            tercer_digito = int(cedula[2])
            if tercer_digito > 5:
                return {
                    'warning': {
                        'title': 'Cédula del representante inválida',
                        'message': 'El tercer dígito debe ser menor a 6.'
                    }
                }
            
            # Algoritmo de validación
            coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
            suma = 0
            
            for i in range(9):
                valor = int(cedula[i]) * coeficientes[i]
                if valor >= 10:
                    valor -= 9
                suma += valor
            
            resultado = suma % 10
            if resultado == 0:
                digito_verificador = 0
            else:
                digito_verificador = 10 - resultado
            
            if digito_verificador != int(cedula[9]):
                return {
                    'warning': {
                        'title': 'Cédula del representante inválida',
                        'message': 'La cédula no es válida. Por favor verifique el número.'
                    }
                }
                
                for i in range(9):
                    valor = int(cedula[i]) * coeficientes[i]
                    if valor >= 10:
                        valor -= 9
                    suma += valor
                
                resultado = suma % 10
                if resultado == 0:
                    digito_verificador = 0
                else:
                    digito_verificador = 10 - resultado
                
                if digito_verificador != int(cedula[9]):
                    raise ValidationError(_('La cédula del representante no es válida. Por favor verifique el número.'))
    
    @api.constrains('porcentaje_discapacidad')
    def _check_porcentaje_discapacidad(self):
        """Valida que el porcentaje de discapacidad esté entre 0 y 100"""
        for socio in self:
            if socio.porcentaje_discapacidad and (socio.porcentaje_discapacidad < 0 or socio.porcentaje_discapacidad > 100):
                raise ValidationError(_('El porcentaje de discapacidad debe estar entre 0 y 100.'))
    
    @api.constrains('fecha_nacimiento', 'fecha_ingreso')
    def _check_fechas(self):
        """Valida que las fechas sean lógicas"""
        for socio in self:
            if socio.fecha_nacimiento and socio.fecha_nacimiento > date.today():
                raise ValidationError(_('La fecha de nacimiento no puede ser futura.'))
            
            if socio.fecha_ingreso > date.today():
                raise ValidationError(_('La fecha de ingreso no puede ser futura.'))
    
    @api.onchange('tiene_discapacidad')
    def _onchange_tiene_discapacidad(self):
        """Limpia campos de discapacidad si no tiene"""
        if not self.tiene_discapacidad:
            self.tipo_discapacidad = False
            self.porcentaje_discapacidad = 0
    
    @api.onchange('estado')
    def _onchange_estado(self):
        """Sincroniza el campo active con el estado"""
        if self.estado in ('inactivo', 'retirado'):
            self.active = False
            if not self.fecha_baja:
                self.fecha_baja = date.today
    
    @api.onchange('es_menor_edad')
    def _onchange_es_menor_edad(self):
        """Limpia campos de representante si es mayor de edad"""
        if not self.es_menor_edad:
            self.representante_nombre = False
            self.representante_cedula = False
            self.representante_relacion = False
        else:
            self.active = True
            self.fecha_baja = False
            self.motivo_baja = False
    
    # === MÉTODOS ===
    def name_get(self):
        """Personaliza el nombre mostrado: Nombre (Cédula)"""
        result = []
        for socio in self:
            name = f"{socio.name} ({socio.cedula})"
            result.append((socio.id, name))
        return result
    
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        """Permite buscar por nombre o cédula"""
        args = args or []
        if name:
            socios = self._search([
                '|',
                ('name', operator, name),
                ('cedula', operator, name)
            ] + args, limit=limit, access_rights_uid=name_get_uid)
            return socios
        return super()._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
    
    def action_marcar_inactivo(self):
        """Acción para marcar socio como inactivo"""
        self.ensure_one()
        self.write({
            'estado': 'inactivo',
            'active': False,
            'fecha_baja': date.today()
        })
    
    def action_reactivar(self):
        """Acción para reactivar un socio"""
        self.ensure_one()
        self.write({
            'estado': 'activo',
            'active': True,
            'fecha_baja': False,
            'motivo_baja': False
        })

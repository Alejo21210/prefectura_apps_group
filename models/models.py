# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import math


# MODELO: CRÉDITO
class CarteraCredito(models.Model):
    _name = 'cartera.credito'
    _description = 'Crédito de Cartera'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha desc, id desc'

    # Información básica
    name = fields.Char(
        string='Número de Crédito',
        required=True,
        copy=False,
        readonly=True,
        default='Nuevo'
    )
    socio_id = fields.Many2one(
        'res.partner',
        string='Socio',
        required=True,
        tracking=True,
        domain=[('is_company', '=', False)]
    )
    garante_id = fields.Many2one(
        'res.partner',
        string='Garante',
        tracking=True,
        domain=[('is_company', '=', False)]
    )
    fecha = fields.Date(
        string='Fecha del Crédito',
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )
    monto = fields.Float(
        string='Monto del Crédito',
        required=True,
        tracking=True,
        digits=(16, 2)
    )
    plazo = fields.Integer(
        string='Plazo (Meses)',
        required=True,
        tracking=True,
        help='Número de meses para pagar el crédito'
    )
    tasa = fields.Float(
        string='Tasa de Interés Anual (%)',
        required=True,
        tracking=True,
        digits=(5, 2),
        help='Tasa de interés anual en porcentaje'
    )
    metodo_amortizacion = fields.Selection([
        ('frances', 'Francés (Cuota Constante)'),
        ('aleman', 'Alemán (Capital Constante)')
    ], string='Método de Amortización',
       required=True,
       default='frances',
       tracking=True
    )
    destino = fields.Text(
        string='Destino del Crédito',
        tracking=True
    )
    
    # Estado
    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('aprobado', 'Aprobado'),
        ('activo', 'Activo'),
        ('pagado', 'Pagado'),
        ('cancelado', 'Cancelado')
    ], string='Estado',
       default='borrador',
       required=True,
       tracking=True
    )
    
    # Relaciones
    cuota_ids = fields.One2many(
        'cartera.cuota',
        'credito_id',
        string='Cuotas'
    )
    pago_ids = fields.One2many(
        'cartera.pago',
        'credito_id',
        string='Pagos'
    )
    
    # Campos computados
    total_a_pagar = fields.Float(
        string='Total a Pagar',
        compute='_compute_indicadores',
        store=True,
        digits=(16, 2)
    )
    total_cobrar = fields.Float(
        string='Total a Cobrar',
        compute='_compute_indicadores',
        store=True,
        digits=(16, 2)
    )
    saldo_por_cobrar = fields.Float(
        string='Saldo por Cobrar',
        compute='_compute_indicadores',
        store=True,
        digits=(16, 2)
    )
    saldo_actual = fields.Float(
        string='Saldo Actual',
        compute='_compute_saldo_actual',
        store=True,
        digits=(16, 2),
        help='Saldo pendiente del capital'
    )
    esta_vencido = fields.Boolean(
        string='Tiene Cuotas Vencidas',
        compute='_compute_esta_vencido',
        store=True
    )
    num_cuotas = fields.Integer(
        string='Número de Cuotas',
        compute='_compute_num_cuotas',
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id
    )
    
    # Constraints
    _sql_constraints = [
        ('monto_positivo', 'CHECK(monto > 0)', 'El monto debe ser mayor a cero.'),
        ('plazo_positivo', 'CHECK(plazo > 0)', 'El plazo debe ser mayor a cero.'),
        ('tasa_positiva', 'CHECK(tasa >= 0)', 'La tasa de interés debe ser mayor o igual a cero.'),
    ]
    
    @api.model_create_multi
    def create(self, vals_list):
        """Generar número de crédito consecutivo"""
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('cartera.credito') or 'Nuevo'
        return super(CarteraCredito, self).create(vals_list)
    
    @api.depends('cuota_ids.monto_total')
    def _compute_indicadores(self):
        """Calcular indicadores del crédito"""
        for credito in self:
            total_a_pagar = sum(credito.cuota_ids.mapped('monto_total'))
            total_cobrado = sum(credito.pago_ids.mapped('monto'))
            credito.total_a_pagar = total_a_pagar
            credito.total_cobrar = total_cobrado
            credito.saldo_por_cobrar = total_a_pagar - total_cobrado
    
    @api.depends('cuota_ids.saldo_pendiente')
    def _compute_saldo_actual(self):
        """Calcular saldo actual del capital"""
        for credito in self:
            saldo = sum(credito.cuota_ids.mapped('saldo_pendiente'))
            credito.saldo_actual = saldo
    
    @api.depends('cuota_ids.estado')
    def _compute_esta_vencido(self):
        """Verificar si tiene cuotas vencidas"""
        for credito in self:
            credito.esta_vencido = any(cuota.estado == 'vencida' for cuota in credito.cuota_ids)
    
    @api.depends('cuota_ids')
    def _compute_num_cuotas(self):
        """Contar número de cuotas generadas"""
        for credito in self:
            credito.num_cuotas = len(credito.cuota_ids)
    
    @api.constrains('garante_id')
    def _check_garante_limite(self):
        """Validar límite de créditos por garante"""
        for credito in self:
            if credito.garante_id:
                limite = int(self.env['ir.config_parameter'].sudo().get_param(
                    'cartera.max_creditos_garante', default=3
                ))
                
                creditos_activos = self.search_count([
                    ('garante_id', '=', credito.garante_id.id),
                    ('state', 'in', ['aprobado', 'activo']),
                    ('id', '!=', credito.id)
                ])
                
                if creditos_activos >= limite:
                    raise ValidationError(
                        f'El garante {credito.garante_id.name} ya tiene {creditos_activos} '
                        f'créditos activos. El límite es {limite}.'
                    )
    
    def action_aprobar(self):
        """Aprobar crédito"""
        for credito in self:
            if credito.state != 'borrador':
                raise UserError('Solo se pueden aprobar créditos en estado borrador.')
            credito.state = 'aprobado'
    
    def action_activar(self):
        """Activar crédito y generar tabla de amortización"""
        for credito in self:
            if credito.state != 'aprobado':
                raise UserError('Solo se pueden activar créditos aprobados.')
            
            if not credito.cuota_ids:
                credito.generar_tabla_amortizacion()
            
            credito.state = 'activo'
    
    def action_cancelar(self):
        """Cancelar crédito"""
        for credito in self:
            if credito.state == 'pagado':
                raise UserError('No se puede cancelar un crédito ya pagado.')
            credito.state = 'cancelado'
    
    def action_view_cuotas(self):
        """Abrir vista de cuotas del crédito"""
        self.ensure_one()
        return {
            'name': f'Cuotas de {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'cartera.cuota',
            'view_mode': 'list,form',
            'domain': [('credito_id', '=', self.id)],
            'context': {'default_credito_id': self.id}
        }
    
    def action_volver_borrador(self):
        """Volver a borrador"""
        for credito in self:
            credito.cuota_ids.unlink()
            credito.state = 'borrador'
    
    def generar_tabla_amortizacion(self):
        """Generar tabla de amortización según el método seleccionado"""
        self.ensure_one()
        
        self.cuota_ids.unlink()
        
        tasa_mensual = self.tasa / 100 / 12
        
        if self.metodo_amortizacion == 'frances':
            self._generar_amortizacion_frances(tasa_mensual)
        elif self.metodo_amortizacion == 'aleman':
            self._generar_amortizacion_aleman(tasa_mensual)
    
    def _generar_amortizacion_frances(self, tasa_mensual):
        """Generar tabla de amortización método francés (cuota constante)"""
        if tasa_mensual == 0:
            cuota_fija = self.monto / self.plazo
        else:
            cuota_fija = self.monto * (tasa_mensual * math.pow(1 + tasa_mensual, self.plazo)) / \
                        (math.pow(1 + tasa_mensual, self.plazo) - 1)
        
        saldo = self.monto
        CuotaObj = self.env['cartera.cuota']
        
        for i in range(1, self.plazo + 1):
            interes = saldo * tasa_mensual
            capital = cuota_fija - interes
            
            if i == self.plazo:
                capital = saldo
                cuota = saldo + interes
            else:
                cuota = cuota_fija
            
            saldo_inicial = saldo
            saldo = saldo - capital
            
            fecha_vencimiento = self.fecha + relativedelta(months=i)
            
            CuotaObj.create({
                'credito_id': self.id,
                'numero_cuota': i,
                'fecha_vencimiento': fecha_vencimiento,
                'monto_capital': capital,
                'monto_interes': interes,
                'monto_total': cuota,
                'saldo_inicial': saldo_inicial,
                'saldo_final': max(0, saldo)
            })
    
    def _generar_amortizacion_aleman(self, tasa_mensual):
        """Generar tabla de amortización método alemán (capital constante)"""
        capital_fijo = self.monto / self.plazo
        
        saldo = self.monto
        CuotaObj = self.env['cartera.cuota']
        
        for i in range(1, self.plazo + 1):
            interes = saldo * tasa_mensual
            capital = capital_fijo
            cuota = capital + interes
            
            saldo_inicial = saldo
            saldo = saldo - capital
            
            fecha_vencimiento = self.fecha + relativedelta(months=i)
            
            CuotaObj.create({
                'credito_id': self.id,
                'numero_cuota': i,
                'fecha_vencimiento': fecha_vencimiento,
                'monto_capital': capital,
                'monto_interes': interes,
                'monto_total': cuota,
                'saldo_inicial': saldo_inicial,
                'saldo_final': max(0, saldo)
            })
    
    @api.model
    def calcular_cartera_vencida(self, fecha_corte=None):
        """Calcular cartera vencida hasta una fecha de corte"""
        if not fecha_corte:
            fecha_corte = fields.Date.context_today(self)
        
        cuotas_vencidas = self.env['cartera.cuota'].search([
            ('fecha_vencimiento', '<', fecha_corte),
            ('estado', 'in', ['pendiente', 'vencida'])
        ])
        
        resultado = {}
        for cuota in cuotas_vencidas:
            mes = cuota.fecha_vencimiento.strftime('%Y-%m')
            if mes not in resultado:
                resultado[mes] = {
                    'periodo': mes,
                    'num_creditos': 0,
                    'monto_vencido': 0,
                    'creditos': set()
                }
            
            resultado[mes]['monto_vencido'] += cuota.saldo_pendiente
            resultado[mes]['creditos'].add(cuota.credito_id.id)
        
        for mes in resultado:
            resultado[mes]['num_creditos'] = len(resultado[mes]['creditos'])
            del resultado[mes]['creditos']
        
        return list(resultado.values())


# MODELO: CUOTA
class CarteraCuota(models.Model):
    _name = 'cartera.cuota'
    _description = 'Cuota de Amortización'
    _order = 'credito_id, numero_cuota'

    # Información básica
    credito_id = fields.Many2one(
        'cartera.credito',
        string='Crédito',
        required=True,
        ondelete='cascade'
    )
    socio_id = fields.Many2one(
        'res.partner',
        string='Socio',
        related='credito_id.socio_id',
        store=True,
        readonly=True
    )
    numero_cuota = fields.Integer(
        string='N° Cuota',
        required=True
    )
    fecha_vencimiento = fields.Date(
        string='Fecha de Vencimiento',
        required=True
    )
    
    # Montos
    monto_capital = fields.Float(
        string='Capital',
        required=True,
        digits=(16, 2)
    )
    monto_interes = fields.Float(
        string='Interés',
        required=True,
        digits=(16, 2)
    )
    monto_total = fields.Float(
        string='Total Cuota',
        required=True,
        digits=(16, 2)
    )
    saldo_inicial = fields.Float(
        string='Saldo Inicial',
        digits=(16, 2),
        help='Saldo del crédito antes de esta cuota'
    )
    saldo_final = fields.Float(
        string='Saldo Final',
        digits=(16, 2),
        help='Saldo del crédito después de esta cuota'
    )
    
    # Pagos
    pago_ids = fields.One2many(
        'cartera.pago',
        'cuota_id',
        string='Pagos'
    )
    
    # Campos computados
    monto_pagado = fields.Float(
        string='Monto Pagado',
        compute='_compute_monto_pagado',
        store=True,
        digits=(16, 2)
    )
    saldo_pendiente = fields.Float(
        string='Saldo Pendiente',
        compute='_compute_saldo_pendiente',
        store=True,
        digits=(16, 2)
    )
    estado = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('parcial', 'Pagada Parcial'),
        ('pagada', 'Pagada'),
        ('vencida', 'Vencida')
    ], string='Estado',
       compute='_compute_estado',
       store=True
    )
    dias_vencido = fields.Integer(
        string='Días Vencido',
        compute='_compute_dias_vencido',
        store=True
    )
    
    @api.depends('pago_ids.monto')
    def _compute_monto_pagado(self):
        """Calcular monto total pagado"""
        for cuota in self:
            cuota.monto_pagado = sum(cuota.pago_ids.mapped('monto'))
    
    @api.depends('monto_total', 'monto_pagado')
    def _compute_saldo_pendiente(self):
        """Calcular saldo pendiente de la cuota"""
        for cuota in self:
            cuota.saldo_pendiente = cuota.monto_total - cuota.monto_pagado
    
    @api.depends('saldo_pendiente', 'fecha_vencimiento')
    def _compute_estado(self):
        """Calcular estado de la cuota"""
        hoy = fields.Date.context_today(self)
        
        for cuota in self:
            if cuota.saldo_pendiente <= 0.01:
                cuota.estado = 'pagada'
            elif cuota.fecha_vencimiento < hoy:
                if cuota.monto_pagado > 0:
                    cuota.estado = 'parcial'
                else:
                    cuota.estado = 'vencida'
            else:
                if cuota.monto_pagado > 0:
                    cuota.estado = 'parcial'
                else:
                    cuota.estado = 'pendiente'
    
    @api.depends('fecha_vencimiento', 'estado')
    def _compute_dias_vencido(self):
        """Calcular días de mora"""
        hoy = fields.Date.context_today(self)
        
        for cuota in self:
            if cuota.estado in ['vencida', 'parcial'] and cuota.fecha_vencimiento < hoy:
                delta = hoy - cuota.fecha_vencimiento
                cuota.dias_vencido = delta.days
            else:
                cuota.dias_vencido = 0
    
    def action_registrar_pago(self):
        """Abrir wizard para registrar pago"""
        self.ensure_one()
        
        return {
            'name': 'Registrar Pago',
            'type': 'ir.actions.act_window',
            'res_model': 'cartera.pago',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_cuota_id': self.id,
                'default_credito_id': self.credito_id.id,
                'default_monto': self.saldo_pendiente,
            }
        }
    
    def name_get(self):
        """Personalizar nombre de visualización"""
        result = []
        for cuota in self:
            name = f'{cuota.credito_id.name} - Cuota {cuota.numero_cuota}'
            result.append((cuota.id, name))
        return result


# MODELO: PAGO
class CarteraPago(models.Model):
    _name = 'cartera.pago'
    _description = 'Pago de Cuota'
    _order = 'fecha desc, id desc'

    # Información básica
    name = fields.Char(
        string='Referencia',
        required=True,
        copy=False,
        readonly=True,
        default='Nuevo'
    )
    credito_id = fields.Many2one(
        'cartera.credito',
        string='Crédito',
        required=True,
        ondelete='cascade'
    )
    cuota_id = fields.Many2one(
        'cartera.cuota',
        string='Cuota',
        required=True,
        ondelete='cascade'
    )
    socio_id = fields.Many2one(
        'res.partner',
        string='Socio',
        related='credito_id.socio_id',
        store=True,
        readonly=True
    )
    fecha = fields.Date(
        string='Fecha de Pago',
        required=True,
        default=fields.Date.context_today
    )
    monto = fields.Float(
        string='Monto Pagado',
        required=True,
        digits=(16, 2)
    )
    comprobante = fields.Char(
        string='Comprobante',
        help='Número de comprobante o referencia bancaria'
    )
    notas = fields.Text(
        string='Notas'
    )
    
    # Campos computados
    es_solo_interes = fields.Boolean(
        string='Es Solo Interés',
        compute='_compute_es_solo_interes',
        store=True,
        help='Indica si el pago cubre solo el interés de la cuota'
    )
    aplicado_a_capital = fields.Float(
        string='Aplicado a Capital',
        compute='_compute_aplicacion',
        store=True,
        digits=(16, 2)
    )
    aplicado_a_interes = fields.Float(
        string='Aplicado a Interés',
        compute='_compute_aplicacion',
        store=True,
        digits=(16, 2)
    )
    
    # Constraints
    _sql_constraints = [
        ('monto_positivo', 'CHECK(monto > 0)', 'El monto del pago debe ser mayor a cero.'),
    ]
    
    @api.model_create_multi
    def create(self, vals_list):
        """Generar número de pago consecutivo y validar"""
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('cartera.pago') or 'Nuevo'
        
        pagos = super(CarteraPago, self).create(vals_list)
        
        for pago in pagos:
            pago._validar_pago()
            pago._verificar_alerta_solo_interes()
        
        return pagos
    
    @api.depends('monto', 'cuota_id.monto_interes')
    def _compute_es_solo_interes(self):
        """Verificar si el pago es solo interés"""
        for pago in self:
            if pago.cuota_id:
                tolerancia = pago.cuota_id.monto_interes * 0.05
                diferencia = abs(pago.monto - pago.cuota_id.monto_interes)
                pago.es_solo_interes = diferencia <= tolerancia
            else:
                pago.es_solo_interes = False
    
    @api.depends('monto', 'cuota_id.monto_interes', 'cuota_id.monto_capital')
    def _compute_aplicacion(self):
        """Calcular distribución del pago entre interés y capital"""
        for pago in self:
            if pago.cuota_id:
                monto_restante = pago.monto
                
                if monto_restante >= pago.cuota_id.monto_interes:
                    pago.aplicado_a_interes = pago.cuota_id.monto_interes
                    monto_restante -= pago.cuota_id.monto_interes
                else:
                    pago.aplicado_a_interes = monto_restante
                    monto_restante = 0
                
                pago.aplicado_a_capital = monto_restante
            else:
                pago.aplicado_a_interes = 0
                pago.aplicado_a_capital = 0
    
    def _validar_pago(self):
        """Validar que el pago no exceda el saldo pendiente"""
        for pago in self:
            if pago.cuota_id:
                otros_pagos = pago.cuota_id.pago_ids.filtered(lambda p: p.id != pago.id)
                monto_otros_pagos = sum(otros_pagos.mapped('monto'))
                saldo_pendiente = pago.cuota_id.monto_total - monto_otros_pagos
                
                if pago.monto > saldo_pendiente + 0.01:
                    raise ValidationError(
                        f'El monto del pago (${pago.monto:.2f}) excede el saldo pendiente '
                        f'de la cuota (${saldo_pendiente:.2f}).'
                    )
                
                if pago.monto < pago.cuota_id.monto_interes:
                    raise UserError(
                        f'Advertencia: El pago (${pago.monto:.2f}) es menor que el interés '
                        f'de la cuota (${pago.cuota_id.monto_interes:.2f}). '
                        f'El pago solo se aplicará parcialmente al interés.'
                    )
    
    def _verificar_alerta_solo_interes(self):
        """Verificar y alertar sobre pagos consecutivos de solo interés"""
        for pago in self:
            if pago.es_solo_interes and pago.credito_id:
                limite = int(self.env['ir.config_parameter'].sudo().get_param(
                    'cartera.alertas_solo_interes', default=3
                ))
                
                pagos_credito = self.search([
                    ('credito_id', '=', pago.credito_id.id),
                    ('es_solo_interes', '=', True)
                ], order='fecha desc')
                
                num_pagos_solo_interes = len(pagos_credito)
                
                if num_pagos_solo_interes >= limite:
                    pago.credito_id.activity_schedule(
                        'mail.mail_activity_data_warning',
                        summary=f'Alerta: {num_pagos_solo_interes} pagos consecutivos de solo interés',
                        note=f'El socio {pago.socio_id.name} ha realizado {num_pagos_solo_interes} '
                             f'pagos consecutivos cubriendo solo el interés del crédito {pago.credito_id.name}. '
                             f'Se recomienda contactar al socio para regularizar la situación.',
                        user_id=self.env.user.id
                    )
                    
                    pago.credito_id.message_post(
                        body=f'⚠️ <b>Alerta de Pago Solo Interés</b><br/>'
                             f'Se han detectado {num_pagos_solo_interes} pagos consecutivos '
                             f'cubriendo solo el interés. Se recomienda seguimiento.',
                        message_type='notification'
                    )
    
    @api.onchange('cuota_id')
    def _onchange_cuota_id(self):
        """Actualizar monto sugerido al cambiar de cuota"""
        if self.cuota_id:
            self.monto = self.cuota_id.saldo_pendiente
            self.credito_id = self.cuota_id.credito_id
    
    def name_get(self):
        """Personalizar nombre de visualización"""
        result = []
        for pago in self:
            name = f'{pago.name} - ${pago.monto:.2f}'
            result.append((pago.id, name))
        return result


# MODELO: CONFIGURACIÓN
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Parámetros de Cartera
    max_creditos_garante = fields.Integer(
        string='Máximo de Créditos por Garante',
        config_parameter='cartera.max_creditos_garante',
        default=3,
        help='Número máximo de créditos activos que puede respaldar un garante'
    )
    
    alertas_solo_interes = fields.Integer(
        string='Alertas de Pagos Solo Interés',
        config_parameter='cartera.alertas_solo_interes',
        default=3,
        help='Número de pagos consecutivos de solo interés antes de generar alerta'
    )
    
    metodo_amortizacion_default = fields.Selection([
        ('frances', 'Francés (Cuota Constante)'),
        ('aleman', 'Alemán (Capital Constante)')
    ], string='Método de Amortización por Defecto',
       config_parameter='cartera.metodo_default',
       default='frances',
       help='Método de amortización que se selecciona por defecto al crear un crédito'
    )

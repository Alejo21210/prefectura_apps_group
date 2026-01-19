# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class EpsEgreso(models.Model):
    #Identificador del modelo
    _name = 'eps.egreso'
    _description = 'Libro Diario de Egresos'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    #DATOS DEL COMPROBANTE 
    name = fields.Char(string='Código', required=True, copy=False, readonly=True, default='Nuevo')
    
    fecha = fields.Date(string='Fecha', required=True, default=fields.Date.context_today, tracking=True)
    
    beneficiario = fields.Char(string='Beneficiario', required=True, tracking=True, 
                              help="Persona que recibe el dinero")
    
    concepto = fields.Char(string='Descripción / Concepto', required=True, tracking=True,
                          help="Ej: Compra de suministros, Préstamo a socio...")
    
    monto = fields.Float(string='Valor de Salida ($)', required=True, digits=(16, 2), tracking=True)

    #CLASIFICACIÓN 
    tipo_egreso = fields.Selection([
        ('gasto', 'Gasto Operativo (Servicios, Suministros)'),
        ('desembolso', 'Desembolso de Crédito (Préstamos)'),
        ('devolucion', 'Devolución de Ahorros')
    ], string='Tipo de Movimiento', required=True, default='gasto', tracking=True)

    #SECTOR DESTINO
    destino_credito = fields.Selection([
        ('comercio', 'Comercio'),
        ('agropecuario', 'Agropecuario'),
        ('produccion', 'Producción'),
        ('servicios', 'Servicios'),
        ('consumo', 'Consumo'),
        ('vivienda', 'Vivienda'),
        ('salud', 'Salud'),
        ('educacion', 'Educación')
    ], string='Sector / Destino', help="Campo obligatorio si es un Desembolso de Crédito")

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('posted', 'Validado'),
        ('cancel', 'Anulado')
    ], string='Estado', default='draft', tracking=True)

    #SECUENCIA AUTOMÁTICA 
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('eps.egreso') or 'Nuevo'
        return super(EpsEgreso, self).create(vals_list)

    #ACCIONES (Validar, Anular, Borrador) 
    def action_validar(self):
        for rec in self:
            if rec.tipo_egreso == 'desembolso' and not rec.destino_credito:
                raise UserError(_("Para desembolsos de crédito, es OBLIGATORIO seleccionar el Sector (Destino)."))
            
            # TODO: Integración Contable (Issue 06)
            rec.state = 'posted'

    def action_borrador(self):
        self.state = 'draft'

    #NUEVA FUNCIÓN: ANULAR 
    def action_cancelar(self):
        for rec in self:
            rec.state = 'cancel'
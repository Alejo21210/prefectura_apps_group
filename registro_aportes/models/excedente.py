from odoo import models, fields, api

class AporteExcedente(models.Model):
    _name = 'aporte.excedente'
    _description = 'Cálculo de Excedentes'

    socio_id = fields.Many2one(
        'res.partner',
        domain=[('es_socio', '=', True)],
        required=True
    )

    anio = fields.Integer(required=True)

    saldo_promedio = fields.Float(string='Saldo Promedio')

    total_promedios = fields.Float(string='Total Promedios')

    porcentaje_total = fields.Float(
        string='% del Total',
        compute='_compute_porcentaje_total',
        store=True
    )

    rendimiento = fields.Float(string='% Rendimiento')

    excedente = fields.Float(
        string='Excedente',
        compute='_compute_excedente',
        store=True
    )

    anticipo = fields.Float(string='Anticipo de excedentes')

    excedente_final = fields.Float(
        string='Excedente final',
        compute='_compute_excedente_final',
        store=True
    )

    @api.depends('saldo_promedio', 'total_promedios')
    def _compute_porcentaje_total(self):
        for rec in self:
            rec.porcentaje_total = (
                (rec.saldo_promedio / rec.total_promedios) * 100
                if rec.total_promedios else 0.0
            )

    @api.depends('saldo_promedio', 'rendimiento')
    def _compute_excedente(self):
        for rec in self:
            rec.excedente = rec.saldo_promedio * (rec.rendimiento / 100)

    @api.depends('excedente', 'anticipo')
    def _compute_excedente_final(self):
        for rec in self:
            rec.excedente_final = rec.excedente - rec.anticipo

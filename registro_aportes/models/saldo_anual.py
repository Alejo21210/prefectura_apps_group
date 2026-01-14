from odoo import models, fields, api

class SaldoAnual(models.Model):
    _name = 'aporte.saldo.anual'
    _description = 'Saldo Anual del Socio'
    _order = 'anio desc'

    socio_id = fields.Many2one(
        'res.partner',
        domain=[('es_socio', '=', True)],
        required=True
    )

    anio = fields.Integer(required=True)

    saldo_inicial = fields.Float(string='Saldo Inicial')

    saldo_diciembre = fields.Float(
        string='Saldo a Diciembre',
        compute='_compute_saldo_diciembre',
        store=True
    )

    saldo_promedio = fields.Float(
        string='Saldo Promedio del Año',
        compute='_compute_saldo_promedio',
        store=True
    )

    cerrado = fields.Boolean(default=False)

    def _compute_saldo_diciembre(self):
        for rec in self:
            dic = self.env['aporte.registro'].search([
                ('socio_id', '=', rec.socio_id.id),
                ('anio', '=', rec.anio),
                ('mes', '=', '12')
            ], limit=1)
            rec.saldo_diciembre = dic.saldo if dic else 0.0

    def _compute_saldo_promedio(self):
        for rec in self:
            registros = self.env['aporte.registro'].search([
                ('socio_id', '=', rec.socio_id.id),
                ('anio', '=', rec.anio)
            ])
            rec.saldo_promedio = (
                sum(r.saldo for r in registros) / len(registros)
                if registros else 0.0
            )

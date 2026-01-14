from odoo import models, fields, api

class AporteRegistro(models.Model):
    _name = 'aporte.registro'
    _description = 'Registro Mensual de Aportes'
    _order = 'anio, mes'

    socio_id = fields.Many2one(
        'res.partner',
        string='Socio',
        domain=[('es_socio', '=', True)],
        required=True
    )

    mes = fields.Selection([
        ('1','Enero'), ('2','Febrero'), ('3','Marzo'),
        ('4','Abril'), ('5','Mayo'), ('6','Junio'),
        ('7','Julio'), ('8','Agosto'), ('9','Septiembre'),
        ('10','Octubre'), ('11','Noviembre'), ('12','Diciembre')
    ], required=True)

    anio = fields.Integer(string='Año', required=True)

    ingreso = fields.Float(string='Ingresos', default=0.0)
    egreso = fields.Float(string='Egresos', default=0.0)

    saldo = fields.Float(
        string='Saldo',
        compute='_compute_saldo',
        store=True
    )

    observacion = fields.Text(string='Observación')

    @api.depends('ingreso', 'egreso', 'mes', 'anio', 'socio_id')
    def _compute_saldo(self):
        for rec in self:
            saldo_anterior = 0.0

            anterior = self.search([
                ('socio_id', '=', rec.socio_id.id),
                ('anio', '=', rec.anio),
                ('mes', '<', rec.mes)
            ], order='mes desc', limit=1)

            if anterior:
                saldo_anterior = anterior.saldo

            rec.saldo = saldo_anterior + rec.ingreso - rec.egreso

    _sql_constraints = [
        ('socio_mes_anio_unico',
         'unique(socio_id, mes, anio)',
         'Ya existe un registro para este socio en ese período')
    ]

from odoo import models, fields

class AporteEgreso(models.Model):
    _name = 'aporte.egreso'
    _description = 'Egresos Extraordinarios'

    socio_id = fields.Many2one(
        'res.partner',
        domain=[('es_socio', '=', True)],
        required=True
    )
    fecha = fields.Date(required=True)
    monto = fields.Float(required=True)
    descripcion = fields.Text()

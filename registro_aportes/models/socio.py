from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    es_socio = fields.Boolean(string='Es socio', default=False)
    codigo_socio = fields.Char(string='Código de socio')

from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'
    eps_caja_ids = fields.Many2many('eps.caja', string='Cajas Asignadas')
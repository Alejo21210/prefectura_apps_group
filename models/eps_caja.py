from odoo import models, fields

class EpsCaja(models.Model):
    _name = 'eps.caja'
    _description = 'Caja de Ahorro EPS'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # === IDENTIDAD VISUAL ===
    name = fields.Char(string='Nombre de la Caja', required=True, tracking=True)
    logo = fields.Binary(string='Logo de la Caja', attachment=True)
    
    # === PARAMETRIZACIÓN ECONÓMICA ===
    currency_id = fields.Many2one('res.currency', string='Moneda', default=lambda self: self.env.company.currency_id)
    
    monto_aporte_minimo = fields.Monetary(string='Cuota de Aporte ($)', help="Valor mensual obligatorio")
    limite_credito_base = fields.Monetary(string='Límite Base de Crédito ($)')
    
    # === REGLAS Y TASAS ===
    tasa_interes_prestamo = fields.Float(string='Tasa Interés Préstamo (%)', digits=(5, 2))
    tasa_mora = fields.Float(string='Tasa de Mora (%)', digits=(5, 2))
    
    regla_garantes = fields.Selection([
        ('1_garante', '1 Garante obligatorio'),
        ('2_garantes', '2 Garantes obligatorios'),
        ('saldo_cuenta', 'Garantía sobre saldo propio')
    ], string='Regla de Garantes', default='1_garante')

    active = fields.Boolean(default=True)
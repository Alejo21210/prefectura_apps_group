from odoo import models, fields

class CierreAnualWizard(models.TransientModel):
    _name = 'aporte.cierre.anual.wizard'
    _description = 'Cierre Anual de Aportes'

    anio = fields.Integer(required=True)

    def action_cerrar_anio(self):
        socios = self.env['res.partner'].search([('es_socio', '=', True)])

        for socio in socios:
            saldo_anual = self.env['aporte.saldo.anual'].search([
                ('socio_id', '=', socio.id),
                ('anio', '=', self.anio)
            ], limit=1)

            if not saldo_anual:
                saldo_anual = self.env['aporte.saldo.anual'].create({
                    'socio_id': socio.id,
                    'anio': self.anio,
                })

            saldo_anual.cerrado = True

            # Crear saldo inicial siguiente año
            self.env['aporte.saldo.anual'].create({
                'socio_id': socio.id,
                'anio': self.anio + 1,
                'saldo_inicial': saldo_anual.saldo_diciembre,
            })

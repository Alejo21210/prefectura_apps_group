# from odoo import http


# class RegistroAportes(http.Controller):
#     @http.route('/registro_aportes/registro_aportes', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/registro_aportes/registro_aportes/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('registro_aportes.listing', {
#             'root': '/registro_aportes/registro_aportes',
#             'objects': http.request.env['registro_aportes.registro_aportes'].search([]),
#         })

#     @http.route('/registro_aportes/registro_aportes/objects/<model("registro_aportes.registro_aportes"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('registro_aportes.object', {
#             'object': obj
#         })


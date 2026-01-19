from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    cartera_role = fields.Selection([
        ('user', 'Usuario'),
        ('manager', 'Gestor'),
        ('admin', 'Administrador'),
    ], string='Rol de Cartera', default='user',
       help="Selecciona el nivel de acceso para el módulo de Cartera de Créditos.")

    @api.model
    def create(self, vals):
        user = super(ResUsers, self).create(vals)
        if 'cartera_role' in vals:
            user._update_cartera_groups(vals['cartera_role'])
        return user

    def write(self, vals):
        if self.env.context.get('cartera_role_update'):
            return super(ResUsers, self).write(vals)
            
        res = super(ResUsers, self).write(vals)
        if 'cartera_role' in vals:
            for user in self:
                user._update_cartera_groups(vals['cartera_role'])
        return res

    def _update_cartera_groups(self, role):
        group_user = self.env.ref('prefectura_ute_6.group_cartera_user')
        group_manager = self.env.ref('prefectura_ute_6.group_cartera_manager')
        group_admin = self.env.ref('prefectura_ute_6.group_cartera_admin')
        
        commands = []
        
        # 1. Remover todos los grupos de cartera
        groups_to_remove = [group_user.id, group_manager.id, group_admin.id]
        for g in groups_to_remove:
            commands.append((3, g))
            
        # 2. Agregar grupos segun rol
        groups_to_add = []
        if role == 'user':
            groups_to_add = [group_user.id]
        elif role == 'manager':
            groups_to_add = [group_user.id, group_manager.id]
        elif role == 'admin':
            groups_to_add = [group_user.id, group_manager.id, group_admin.id]
            
        for g in groups_to_add:
            commands.append((4, g))
            
        if commands:
            self.sudo().with_context(cartera_role_update=True).write({'group_ids': commands})

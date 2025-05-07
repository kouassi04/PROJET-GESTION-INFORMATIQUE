from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SoftwareCategory(models.Model):
    _name = 'parc_it.software.category'
    _description = 'Catégorie de logiciel'
    _order = 'name'

    name = fields.Char(string='Nom', required=True)
    description = fields.Text(string='Description')
    software_count = fields.Integer(compute='_compute_software_count', string='Nombre de logiciels')
    
    @api.depends()
    def _compute_software_count(self):
        for record in self:
            record.software_count = self.env['parc_it.software'].search_count([
                ('category_id', '=', record.id)
            ])


class Software(models.Model):
    _name = 'parc_it.software'
    _description = 'Logiciel'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Nom', required=True, tracking=True)
    version = fields.Char(string='Version', tracking=True)
    publisher = fields.Char(string='Éditeur', tracking=True)
    category_id = fields.Many2one('parc_it.software.category', string='Catégorie', tracking=True)
    description = fields.Text(string='Description')
    
    license_key = fields.Char(string='Clé de licence', tracking=True)
    license_type = fields.Selection([
        ('perpetual', 'Perpétuelle'),
        ('subscription', 'Abonnement'),
        ('free', 'Gratuit'),
        ('open_source', 'Open Source'),
    ], string='Type de licence', default='subscription', tracking=True)
    
    start_date = fields.Date(string='Date de début', tracking=True)
    expiration_date = fields.Date(string='Date d\'expiration', tracking=True)
    
    max_users = fields.Integer(string='Utilisateurs maximum', tracking=True)
    current_users = fields.Integer(compute='_compute_current_users', string='Utilisateurs actuels')
    
    equipment_ids = fields.Many2many('parc_it.equipment', 'equipment_software_rel', 'software_id', 'equipment_id', string='Équipements')
    equipment_count = fields.Integer(compute='_compute_equipment_count', string='Nombre d\'équipements')
    
    contract_id = fields.Many2one('parc_it.contract', string='Contrat associé', tracking=True)
    client_id = fields.Many2one('res.partner', string='Client', domain=[('is_company', '=', True)], tracking=True)
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('expiring_soon', 'Expiration proche'),
        ('expired', 'Expiré'),
    ], string='État', compute='_compute_state', store=True, tracking=True)
    
    notes = fields.Html(string='Notes')
    active = fields.Boolean(default=True, string='Actif')
    
    @api.depends('equipment_ids')
    def _compute_equipment_count(self):
        for record in self:
            record.equipment_count = len(record.equipment_ids)
    
    @api.depends('equipment_ids')
    def _compute_current_users(self):
        for record in self:
            record.current_users = len(record.equipment_ids)
    
    @api.depends('expiration_date')
    def _compute_state(self):
        today = fields.Date.today()
        for record in self:
            if not record.expiration_date:
                record.state = 'active'
                continue
                
            if record.expiration_date < today:
                record.state = 'expired'
            elif record.expiration_date < today + fields.Duration(days=30):
                record.state = 'expiring_soon'
            else:
                record.state = 'active'
    
    def action_view_equipment(self):
        self.ensure_one()
        return {
            'name': _('Équipements'),
            'view_mode': 'tree,form',
            'res_model': 'parc_it.equipment',
            'domain': [('id', 'in', self.equipment_ids.ids)],
            'type': 'ir.actions.act_window',
        } 
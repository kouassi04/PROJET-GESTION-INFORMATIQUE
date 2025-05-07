from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EquipmentType(models.Model):
    _name = 'parc_it.equipment.type'
    _description = 'Type d\'équipement'
    _order = 'name'

    name = fields.Char(string='Nom', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')
    equipment_count = fields.Integer(compute='_compute_equipment_count', string='Nombre d\'équipements')
    
    @api.depends()
    def _compute_equipment_count(self):
        for record in self:
            record.equipment_count = self.env['parc_it.equipment'].search_count([
                ('type_id', '=', record.id)
            ])


class Equipment(models.Model):
    _name = 'parc_it.equipment'
    _description = 'Équipement informatique'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Nom', required=True, tracking=True)
    serial_number = fields.Char(string='Numéro de série', tracking=True)
    reference = fields.Char(string='Référence', tracking=True)
    type_id = fields.Many2one('parc_it.equipment.type', string='Type d\'équipement', required=True, tracking=True)
    client_id = fields.Many2one('res.partner', string='Client', domain=[('is_company', '=', True)], tracking=True)
    employee_id = fields.Many2one('res.partner', string='Utilisateur', domain=[('is_company', '=', False)], tracking=True)
    purchase_date = fields.Date(string='Date d\'achat', tracking=True)
    warranty_end_date = fields.Date(string='Fin de garantie', tracking=True)
    installation_date = fields.Date(string='Date d\'installation', tracking=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('in_stock', 'En stock'),
        ('assigned', 'Assigné'),
        ('in_maintenance', 'En maintenance'),
        ('end_of_life', 'Fin de vie'),
    ], string='État', default='draft', tracking=True)
    
    contract_id = fields.Many2one('parc_it.contract', string='Contrat associé', tracking=True)
    location = fields.Char(string='Emplacement', tracking=True)
    model = fields.Char(string='Modèle', tracking=True)
    manufacturer = fields.Char(string='Fabricant', tracking=True)
    notes = fields.Html(string='Notes')
    
    intervention_ids = fields.One2many('parc_it.intervention', 'equipment_id', string='Interventions')
    intervention_count = fields.Integer(compute='_compute_intervention_count', string='Nombre d\'interventions')
    
    installed_software_ids = fields.Many2many('parc_it.software', 'equipment_software_rel', 'equipment_id', 'software_id', string='Logiciels installés')
    installed_software_count = fields.Integer(compute='_compute_installed_software_count', string='Nombre de logiciels')
    
    image = fields.Binary(string='Image', attachment=True)
    active = fields.Boolean(default=True, string='Actif')
    
    @api.depends('intervention_ids')
    def _compute_intervention_count(self):
        for record in self:
            record.intervention_count = len(record.intervention_ids)
    
    @api.depends('installed_software_ids')
    def _compute_installed_software_count(self):
        for record in self:
            record.installed_software_count = len(record.installed_software_ids)
    
    def action_view_interventions(self):
        self.ensure_one()
        return {
            'name': _('Interventions'),
            'view_mode': 'tree,form',
            'res_model': 'parc_it.intervention',
            'domain': [('equipment_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_equipment_id': self.id}
        }
    
    def action_view_installed_software(self):
        self.ensure_one()
        return {
            'name': _('Logiciels installés'),
            'view_mode': 'tree,form',
            'res_model': 'parc_it.software',
            'domain': [('id', 'in', self.installed_software_ids.ids)],
            'type': 'ir.actions.act_window',
        }
    
    def action_assign(self):
        self.write({'state': 'assigned'})
    
    def action_set_in_maintenance(self):
        self.write({'state': 'in_maintenance'})
    
    def action_set_in_stock(self):
        self.write({'state': 'in_stock'})
    
    def action_set_end_of_life(self):
        self.write({'state': 'end_of_life'})
    
    @api.model_create_multi
    def create(self, vals_list):
        equipments = super(Equipment, self).create(vals_list)
        for equipment in equipments:
            equipment.message_post(body=_("Équipement créé"))
        return equipments 
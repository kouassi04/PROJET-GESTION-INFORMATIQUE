from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_it_client = fields.Boolean(string='Client IT', default=False,
                               help="Cocher si ce partenaire est un client pour les services informatiques")
    
    equipment_ids = fields.One2many('parc_it.equipment', 'client_id', string='Équipements')
    equipment_count = fields.Integer(compute='_compute_equipment_count', string='Nombre d\'équipements')
    
    software_ids = fields.One2many('parc_it.software', 'client_id', string='Logiciels')
    software_count = fields.Integer(compute='_compute_software_count', string='Nombre de logiciels')
    
    contract_ids = fields.One2many('parc_it.contract', 'client_id', string='Contrats')
    contract_count = fields.Integer(compute='_compute_contract_count', string='Nombre de contrats')
    
    intervention_ids = fields.One2many('parc_it.intervention', 'client_id', string='Interventions')
    intervention_count = fields.Integer(compute='_compute_intervention_count', string='Nombre d\'interventions')
    
    # Champs spécifiques pour les clients IT
    it_manager = fields.Char(string='Responsable IT')
    it_manager_email = fields.Char(string='Email du responsable IT')
    it_manager_phone = fields.Char(string='Téléphone du responsable IT')
    
    @api.depends('equipment_ids')
    def _compute_equipment_count(self):
        for partner in self:
            partner.equipment_count = len(partner.equipment_ids)
    
    @api.depends('software_ids')
    def _compute_software_count(self):
        for partner in self:
            partner.software_count = len(partner.software_ids)
    
    @api.depends('contract_ids')
    def _compute_contract_count(self):
        for partner in self:
            partner.contract_count = len(partner.contract_ids)
    
    @api.depends('intervention_ids')
    def _compute_intervention_count(self):
        for partner in self:
            partner.intervention_count = len(partner.intervention_ids)
    
    def action_view_equipment(self):
        self.ensure_one()
        return {
            'name': _('Équipements'),
            'view_mode': 'tree,form',
            'res_model': 'parc_it.equipment',
            'domain': [('client_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_client_id': self.id}
        }
    
    def action_view_software(self):
        self.ensure_one()
        return {
            'name': _('Logiciels'),
            'view_mode': 'tree,form',
            'res_model': 'parc_it.software',
            'domain': [('client_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_client_id': self.id}
        }
    
    def action_view_contracts(self):
        self.ensure_one()
        return {
            'name': _('Contrats'),
            'view_mode': 'tree,form',
            'res_model': 'parc_it.contract',
            'domain': [('client_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_client_id': self.id}
        }
    
    def action_view_interventions(self):
        self.ensure_one()
        return {
            'name': _('Interventions'),
            'view_mode': 'tree,form',
            'res_model': 'parc_it.intervention',
            'domain': [('client_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_client_id': self.id}
        } 
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ContractType(models.Model):
    _name = 'parc_it.contract.type'
    _description = 'Type de contrat'
    _order = 'name'

    name = fields.Char(string='Nom', required=True)
    description = fields.Text(string='Description')
    contract_count = fields.Integer(compute='_compute_contract_count', string='Nombre de contrats')
    
    @api.depends()
    def _compute_contract_count(self):
        for record in self:
            record.contract_count = self.env['parc_it.contract'].search_count([
                ('type_id', '=', record.id)
            ])


class Contract(models.Model):
    _name = 'parc_it.contract'
    _description = 'Contrat de service'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Nom', required=True, tracking=True)
    reference = fields.Char(string='Référence', tracking=True)
    type_id = fields.Many2one('parc_it.contract.type', string='Type de contrat', required=True, tracking=True)
    client_id = fields.Many2one('res.partner', string='Client', domain=[('is_company', '=', True)], required=True, tracking=True)
    
    # Le module sale_subscription a changé dans Odoo 18, cette référence n'est plus valide
    # subscription_id = fields.Many2one('sale.subscription', string='Abonnement associé', tracking=True,
    #                                  help="Abonnement pour la facturation récurrente")
    
    start_date = fields.Date(string='Date de début', required=True, tracking=True)
    end_date = fields.Date(string='Date de fin', tracking=True)
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('pending', 'En attente'),
        ('active', 'Actif'),
        ('expiring_soon', 'Expiration proche'),
        ('expired', 'Expiré'),
        ('cancelled', 'Annulé'),
    ], string='État', compute='_compute_state', store=True, tracking=True)
    
    equipment_ids = fields.One2many('parc_it.equipment', 'contract_id', string='Équipements')
    equipment_count = fields.Integer(compute='_compute_equipment_count', string='Nombre d\'équipements')
    
    software_ids = fields.One2many('parc_it.software', 'contract_id', string='Logiciels')
    software_count = fields.Integer(compute='_compute_software_count', string='Nombre de logiciels')
    
    intervention_ids = fields.One2many('parc_it.intervention', 'contract_id', string='Interventions')
    intervention_count = fields.Integer(compute='_compute_intervention_count', string='Nombre d\'interventions')
    
    description = fields.Html(string='Description')
    attachment_ids = fields.Many2many('ir.attachment', string='Pièces jointes')
    
    billing_frequency = fields.Selection([
        ('monthly', 'Mensuelle'),
        ('quarterly', 'Trimestrielle'),
        ('semi_annual', 'Semestrielle'),
        ('annual', 'Annuelle'),
    ], string='Fréquence de facturation', default='monthly', tracking=True)
    
    next_invoice_date = fields.Date(string='Prochaine date de facturation', compute='_compute_next_invoice_date', store=True)
    
    maintenance_included = fields.Boolean(string='Maintenance incluse', default=True, tracking=True)
    support_hours = fields.Float(string='Heures de support incluses', tracking=True)
    support_hours_used = fields.Float(string='Heures de support utilisées', compute='_compute_support_hours_used')
    support_hours_remaining = fields.Float(string='Heures de support restantes', compute='_compute_support_hours_remaining')
    
    active = fields.Boolean(default=True, string='Actif')
    
    @api.depends('end_date')
    def _compute_state(self):
        today = fields.Date.today()
        for record in self:
            if record.state == 'cancelled':
                continue
                
            if not record.end_date:
                record.state = 'active'
                continue
                
            if record.end_date < today:
                record.state = 'expired'
            elif record.end_date < today + fields.Duration(days=30):
                record.state = 'expiring_soon'
            elif record.start_date <= today:
                record.state = 'active'
            elif record.start_date > today:
                record.state = 'pending'
            else:
                record.state = 'draft'
    
    @api.depends('equipment_ids')
    def _compute_equipment_count(self):
        for record in self:
            record.equipment_count = len(record.equipment_ids)
    
    @api.depends('software_ids')
    def _compute_software_count(self):
        for record in self:
            record.software_count = len(record.software_ids)
    
    @api.depends('intervention_ids')
    def _compute_intervention_count(self):
        for record in self:
            record.intervention_count = len(record.intervention_ids)
    
    @api.depends('start_date', 'billing_frequency')
    def _compute_next_invoice_date(self):
        for record in self:
            if not record.start_date:
                record.next_invoice_date = False
                continue
                
            today = fields.Date.today()
            next_date = record.start_date
            
            # Trouver la prochaine date de facturation basée sur la fréquence
            while next_date <= today:
                if record.billing_frequency == 'monthly':
                    next_date = next_date + fields.Duration(months=1)
                elif record.billing_frequency == 'quarterly':
                    next_date = next_date + fields.Duration(months=3)
                elif record.billing_frequency == 'semi_annual':
                    next_date = next_date + fields.Duration(months=6)
                elif record.billing_frequency == 'annual':
                    next_date = next_date + fields.Duration(years=1)
            
            record.next_invoice_date = next_date
    
    @api.depends('intervention_ids.hours_spent', 'intervention_ids.state')
    def _compute_support_hours_used(self):
        for record in self:
            record.support_hours_used = sum(
                intervention.hours_spent for intervention in record.intervention_ids 
                if intervention.state == 'done' and intervention.type == 'support'
            )
    
    @api.depends('support_hours', 'support_hours_used')
    def _compute_support_hours_remaining(self):
        for record in self:
            record.support_hours_remaining = record.support_hours - record.support_hours_used
    
    def action_view_equipment(self):
        self.ensure_one()
        return {
            'name': _('Équipements'),
            'view_mode': 'tree,form',
            'res_model': 'parc_it.equipment',
            'domain': [('contract_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_contract_id': self.id, 'default_client_id': self.client_id.id}
        }
    
    def action_view_software(self):
        self.ensure_one()
        return {
            'name': _('Logiciels'),
            'view_mode': 'tree,form',
            'res_model': 'parc_it.software',
            'domain': [('contract_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_contract_id': self.id, 'default_client_id': self.client_id.id}
        }
    
    def action_view_interventions(self):
        self.ensure_one()
        return {
            'name': _('Interventions'),
            'view_mode': 'tree,form',
            'res_model': 'parc_it.intervention',
            'domain': [('contract_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_contract_id': self.id, 'default_client_id': self.client_id.id}
        }
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_reactivate(self):
        self.write({'state': 'draft'})
        # Recalculer l'état après réactivation
        self._compute_state()
    
    def action_create_subscription(self):
        # TODO: Implémenter la création d'un abonnement pour la facturation récurrente
        pass
    
    def action_generate_invoice(self):
        # TODO: Implémenter la génération manuelle d'une facture
        pass 
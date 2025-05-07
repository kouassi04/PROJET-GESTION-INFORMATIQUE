from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class InterventionType(models.Model):
    _name = 'parc_it.intervention.type'
    _description = 'Type d\'intervention'
    _order = 'name'

    name = fields.Char(string='Nom', required=True)
    description = fields.Text(string='Description')
    intervention_count = fields.Integer(compute='_compute_intervention_count', string='Nombre d\'interventions')
    
    @api.depends()
    def _compute_intervention_count(self):
        for record in self:
            record.intervention_count = self.env['parc_it.intervention'].search_count([
                ('type_id', '=', record.id)
            ])


class Intervention(models.Model):
    _name = 'parc_it.intervention'
    _description = 'Intervention'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string='Titre', required=True, tracking=True)
    reference = fields.Char(string='Référence', tracking=True)
    
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True, tracking=True)
    scheduled_date = fields.Datetime(string='Date planifiée', tracking=True)
    completion_date = fields.Datetime(string='Date de réalisation', tracking=True)
    
    client_id = fields.Many2one('res.partner', string='Client', domain=[('is_company', '=', True)], required=True, tracking=True)
    equipment_id = fields.Many2one('parc_it.equipment', string='Équipement', tracking=True,
                                  domain="[('client_id', '=', client_id)]")
    contract_id = fields.Many2one('parc_it.contract', string='Contrat associé', tracking=True,
                                 domain="[('client_id', '=', client_id)]")
    
    type_id = fields.Many2one('parc_it.intervention.type', string='Type d\'intervention', tracking=True)
    type = fields.Selection([
        ('installation', 'Installation'),
        ('support', 'Support'),
        ('maintenance', 'Maintenance'),
        ('repair', 'Réparation'),
        ('upgrade', 'Mise à niveau'),
    ], string='Catégorie', required=True, default='support', tracking=True)
    
    priority = fields.Selection([
        ('0', 'Basse'),
        ('1', 'Normale'),
        ('2', 'Élevée'),
        ('3', 'Urgente'),
    ], string='Priorité', default='1', tracking=True)
    
    technician_id = fields.Many2one('hr.employee', string='Technicien', tracking=True)
    hours_planned = fields.Float(string='Heures prévues', tracking=True)
    hours_spent = fields.Float(string='Heures passées', tracking=True)
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('scheduled', 'Planifié'),
        ('in_progress', 'En cours'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string='État', default='draft', tracking=True)
    
    description = fields.Html(string='Description')
    resolution = fields.Html(string='Résolution')
    
    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket d\'assistance',
                                       help="Ticket d'assistance associé", tracking=True)
    
    @api.onchange('client_id')
    def _onchange_client_id(self):
        """Réinitialiser les champs dépendants lorsque le client change"""
        self.equipment_id = False
        self.contract_id = False
    
    @api.onchange('equipment_id')
    def _onchange_equipment_id(self):
        """Définir le contrat associé à l'équipement si disponible"""
        if self.equipment_id and self.equipment_id.contract_id:
            self.contract_id = self.equipment_id.contract_id
    
    def action_schedule(self):
        self.write({'state': 'scheduled'})
    
    def action_start(self):
        self.write({'state': 'in_progress'})
    
    def action_done(self):
        self.write({
            'state': 'done',
            'completion_date': fields.Datetime.now()
        })
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
    
    def action_create_ticket(self):
        """Créer un ticket d'assistance à partir de l'intervention"""
        # TODO: Implémenter la création d'un ticket d'assistance
        pass
    
    @api.model_create_multi
    def create(self, vals_list):
        result = []
        for vals in vals_list:
            # Générer une référence automatique si non fournie
            if not vals.get('reference'):
                vals['reference'] = self.env['ir.sequence'].next_by_code('parc_it.intervention') or _('Nouvelle intervention')
        return super(Intervention, self).create(vals_list) 
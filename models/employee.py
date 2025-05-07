from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    is_technician = fields.Boolean(string='Est technicien', default=False,
                               help="Cocher si cet employé est un technicien pour les interventions IT")
    
    intervention_ids = fields.One2many('parc_it.intervention', 'technician_id', string='Interventions')
    intervention_count = fields.Integer(compute='_compute_intervention_count', string='Nombre d\'interventions')
    
    # Compétences techniques
    technical_skill_ids = fields.Many2many('parc_it.technician.skill', string='Compétences techniques')
    
    @api.depends('intervention_ids')
    def _compute_intervention_count(self):
        for employee in self:
            employee.intervention_count = len(employee.intervention_ids)
    
    def action_view_interventions(self):
        self.ensure_one()
        return {
            'name': _('Interventions'),
            'view_mode': 'tree,form',
            'res_model': 'parc_it.intervention',
            'domain': [('technician_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_technician_id': self.id}
        }


class TechnicianSkill(models.Model):
    _name = 'parc_it.technician.skill'
    _description = 'Compétence technique'
    _order = 'name'
    
    name = fields.Char(string='Nom', required=True)
    description = fields.Text(string='Description')
    color = fields.Integer(string='Couleur')
    
    employee_ids = fields.Many2many('hr.employee', string='Techniciens')
    employee_count = fields.Integer(compute='_compute_employee_count', string='Nombre de techniciens')
    
    @api.depends('employee_ids')
    def _compute_employee_count(self):
        for skill in self:
            skill.employee_count = len(skill.employee_ids) 
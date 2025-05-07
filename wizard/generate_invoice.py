from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class GenerateInvoiceWizard(models.TransientModel):
    _name = 'parc_it.generate.invoice.wizard'
    _description = 'Assistant de génération de facture'

    contract_ids = fields.Many2many('parc_it.contract', string='Contrats', required=True,
                                  domain="[('state', 'in', ['active', 'expiring_soon'])]")
    date_invoice = fields.Date(string='Date de facturation', default=fields.Date.context_today, required=True)
    invoice_line_ids = fields.One2many('parc_it.generate.invoice.line.wizard', 'wizard_id', string='Lignes de facturation')
    
    @api.onchange('contract_ids')
    def _onchange_contract_ids(self):
        """Générer les lignes de facturation basées sur les contrats sélectionnés"""
        lines = []
        for contract in self.contract_ids:
            # Créer une ligne pour le contrat de base
            line = {
                'contract_id': contract.id,
                'name': _('Maintenance et support informatique - %s') % contract.name,
                'quantity': 1.0,
                'price_unit': 0.0,  # Sera calculé ou rempli manuellement
            }
            lines.append((0, 0, line))
            
            # Ajouter des lignes pour les équipements si nécessaire
            if contract.equipment_ids:
                line = {
                    'contract_id': contract.id,
                    'name': _('Gestion de parc matériel - %s équipements') % len(contract.equipment_ids),
                    'quantity': len(contract.equipment_ids),
                    'price_unit': 0.0,  # Sera calculé ou rempli manuellement
                }
                lines.append((0, 0, line))
                
            # Ajouter des lignes pour les logiciels si nécessaire
            if contract.software_ids:
                line = {
                    'contract_id': contract.id,
                    'name': _('Gestion des licences - %s logiciels') % len(contract.software_ids),
                    'quantity': len(contract.software_ids),
                    'price_unit': 0.0,  # Sera calculé ou rempli manuellement
                }
                lines.append((0, 0, line))
                
        self.invoice_line_ids = lines
    
    def action_generate_invoices(self):
        """Générer les factures basées sur les informations du wizard"""
        invoices = self.env['account.move']
        for contract in self.contract_ids:
            # Regrouper les lignes par contrat
            contract_lines = self.invoice_line_ids.filtered(lambda l: l.contract_id.id == contract.id)
            if not contract_lines:
                continue
                
            # Créer la facture
            invoice_vals = {
                'partner_id': contract.client_id.id,
                'move_type': 'out_invoice',
                'invoice_date': self.date_invoice,
                'invoice_origin': contract.name,
                'ref': _('Contrat: %s') % contract.reference or contract.name,
                'invoice_line_ids': [],
            }
            
            # Ajouter les lignes de facturation
            for line in contract_lines:
                if line.price_unit <= 0:
                    continue
                    
                product = line.product_id
                account = product.property_account_income_id or product.categ_id.property_account_income_categ_id
                
                invoice_line_vals = {
                    'name': line.name,
                    'product_id': product.id,
                    'account_id': account.id,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                }
                invoice_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))
            
            # Créer la facture seulement s'il y a des lignes valides
            if invoice_vals['invoice_line_ids']:
                invoice = self.env['account.move'].create(invoice_vals)
                invoices += invoice
                
                # Mettre à jour la date de prochaine facturation sur le contrat
                contract.next_invoice_date = self.date_invoice
        
        # Afficher le résultat
        if invoices:
            action = {
                'name': _('Factures générées'),
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', invoices.ids)],
            }
            return action
        else:
            raise ValidationError(_("Aucune facture n'a pu être générée. Vérifiez que les prix unitaires sont correctement définis."))


class GenerateInvoiceLineWizard(models.TransientModel):
    _name = 'parc_it.generate.invoice.line.wizard'
    _description = 'Ligne d\'assistant de génération de facture'

    wizard_id = fields.Many2one('parc_it.generate.invoice.wizard', string='Assistant')
    contract_id = fields.Many2one('parc_it.contract', string='Contrat', required=True)
    name = fields.Char(string='Description', required=True)
    product_id = fields.Many2one('product.product', string='Produit', 
                             domain="[('type', '=', 'service')]", required=True)
    quantity = fields.Float(string='Quantité', default=1.0)
    price_unit = fields.Float(string='Prix unitaire') 
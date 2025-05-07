from collections import OrderedDict

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class CustomerPortalParcIT(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        equipment_count = 0
        software_count = 0
        contract_count = 0
        intervention_count = 0

        if 'equipment_count' in counters:
            equipment_count = request.env['parc_it.equipment'].search_count([
                ('client_id', '=', partner.commercial_partner_id.id)
            ])
        if 'software_count' in counters:
            software_count = request.env['parc_it.software'].search_count([
                ('client_id', '=', partner.commercial_partner_id.id)
            ])
        if 'contract_count' in counters:
            contract_count = request.env['parc_it.contract'].search_count([
                ('client_id', '=', partner.commercial_partner_id.id)
            ])
        if 'intervention_count' in counters:
            intervention_count = request.env['parc_it.intervention'].search_count([
                ('client_id', '=', partner.commercial_partner_id.id)
            ])

        values.update({
            'equipment_count': equipment_count,
            'software_count': software_count,
            'contract_count': contract_count,
            'intervention_count': intervention_count,
        })
        return values

    # Équipements
    @http.route(['/my/equipment', '/my/equipment/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_equipment(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        Equipment = request.env['parc_it.equipment']

        domain = [
            ('client_id', '=', partner.commercial_partner_id.id)
        ]

        searchbar_sortings = {
            'name': {'label': _('Nom'), 'order': 'name'},
            'date': {'label': _('Date d\'installation'), 'order': 'installation_date desc'},
        }

        searchbar_filters = {
            'all': {'label': _('Tous'), 'domain': []},
            'assigned': {'label': _('Assignés'), 'domain': [('state', '=', 'assigned')]},
            'maintenance': {'label': _('En maintenance'), 'domain': [('state', '=', 'in_maintenance')]},
        }

        # default sortby order
        if not sortby:
            sortby = 'name'
        sort_order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # count for pager
        equipment_count = Equipment.search_count(domain)

        # make pager
        pager = portal_pager(
            url="/my/equipment",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=equipment_count,
            page=page,
            step=self._items_per_page
        )

        # search the records to display
        equipment = Equipment.search(
            domain,
            order=sort_order,
            limit=self._items_per_page,
            offset=pager['offset']
        )

        values.update({
            'equipment': equipment,
            'page_name': 'equipment',
            'pager': pager,
            'default_url': '/my/equipment',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("parc_IT.portal_my_equipment", values)

    @http.route(['/my/equipment/<int:equipment_id>'], type='http', auth="user", website=True)
    def portal_my_equipment_detail(self, equipment_id, **kw):
        equipment = request.env['parc_it.equipment'].browse(equipment_id)
        
        if not equipment or equipment.client_id != request.env.user.partner_id.commercial_partner_id:
            return request.redirect('/my/equipment')
            
        values = {
            'equipment': equipment,
            'page_name': 'equipment',
        }
        return request.render("parc_IT.portal_equipment_detail", values)

    # Interventions
    @http.route(['/my/interventions', '/my/interventions/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_interventions(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        Intervention = request.env['parc_it.intervention']

        domain = [
            ('client_id', '=', partner.commercial_partner_id.id)
        ]

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'date desc'},
            'name': {'label': _('Titre'), 'order': 'name'},
            'state': {'label': _('État'), 'order': 'state'},
        }

        searchbar_filters = {
            'all': {'label': _('Tous'), 'domain': []},
            'scheduled': {'label': _('Planifiées'), 'domain': [('state', '=', 'scheduled')]},
            'in_progress': {'label': _('En cours'), 'domain': [('state', '=', 'in_progress')]},
            'done': {'label': _('Terminées'), 'domain': [('state', '=', 'done')]},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # count for pager
        intervention_count = Intervention.search_count(domain)

        # make pager
        pager = portal_pager(
            url="/my/interventions",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=intervention_count,
            page=page,
            step=self._items_per_page
        )

        # search the records to display
        interventions = Intervention.search(
            domain,
            order=sort_order,
            limit=self._items_per_page,
            offset=pager['offset']
        )

        values.update({
            'interventions': interventions,
            'page_name': 'interventions',
            'pager': pager,
            'default_url': '/my/interventions',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("parc_IT.portal_my_interventions", values)

    @http.route(['/my/interventions/<int:intervention_id>'], type='http', auth="user", website=True)
    def portal_my_intervention_detail(self, intervention_id, **kw):
        intervention = request.env['parc_it.intervention'].browse(intervention_id)
        
        if not intervention or intervention.client_id != request.env.user.partner_id.commercial_partner_id:
            return request.redirect('/my/interventions')
            
        values = {
            'intervention': intervention,
            'page_name': 'interventions',
        }
        return request.render("parc_IT.portal_intervention_detail", values)

    # Contrats
    @http.route(['/my/contracts', '/my/contracts/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_contracts(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        Contract = request.env['parc_it.contract']

        domain = [
            ('client_id', '=', partner.commercial_partner_id.id)
        ]

        searchbar_sortings = {
            'name': {'label': _('Nom'), 'order': 'name'},
            'date': {'label': _('Date'), 'order': 'start_date desc'},
            'state': {'label': _('État'), 'order': 'state'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        # count for pager
        contract_count = Contract.search_count(domain)

        # make pager
        pager = portal_pager(
            url="/my/contracts",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=contract_count,
            page=page,
            step=self._items_per_page
        )

        # search the records to display
        contracts = Contract.search(
            domain,
            order=sort_order,
            limit=self._items_per_page,
            offset=pager['offset']
        )

        values.update({
            'contracts': contracts,
            'page_name': 'contracts',
            'pager': pager,
            'default_url': '/my/contracts',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("parc_IT.portal_my_contracts", values)

    @http.route(['/my/contracts/<int:contract_id>'], type='http', auth="user", website=True)
    def portal_my_contract_detail(self, contract_id, **kw):
        contract = request.env['parc_it.contract'].browse(contract_id)
        
        if not contract or contract.client_id != request.env.user.partner_id.commercial_partner_id:
            return request.redirect('/my/contracts')
            
        values = {
            'contract': contract,
            'page_name': 'contracts',
        }
        return request.render("parc_IT.portal_contract_detail", values) 
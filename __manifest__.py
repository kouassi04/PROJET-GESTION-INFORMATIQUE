{
    'name': 'Gestion de Parc Informatique',
    'version': '1.0',
    'category': 'Services/IT',
    'summary': 'Gestion de parc informatique pour prestataire de services IT',
    'description': """
        Module de gestion de parc informatique avec facturation récurrente intégrée.
        Fonctionnalités principales:
        - Gestion des équipements informatiques (matériel et logiciel)
        - Suivi des interventions et incidents
        - Gestion des contrats de service
        - Facturation récurrente automatisée
        - Portail client pour consultation du parc et signalement d'incidents
    """,
    'author': 'Votre Société',
    'website': 'https://www.votresociete.com',
    'depends': [
        'base',
        'mail',
        'account',
        'helpdesk',
        'stock',
        'hr',
        'portal',
        'product',
    ],
    'data': [
        'security/parc_it_security.xml',
        'security/ir.model.access.csv',
        'data/parc_it_data.xml',
        'views/equipment_views.xml',
        'views/software_views.xml',
        'views/contract_views.xml',
        'views/intervention_views.xml',
        'views/client_views.xml',
        'views/employee_views.xml',
        'views/menu_views.xml',
        'wizard/generate_invoice_views.xml',
        'report/equipment_report.xml',
        'report/intervention_report.xml',
        'report/contract_report.xml',
    ],
    'demo': [
        'demo/parc_it_demo.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            'parc_IT/static/src/scss/parc_it.scss',
            'parc_IT/static/src/js/parc_it.js',
        ],
        'web.assets_frontend': [
            # Temporairement désactivé pour cause d'incompatibilité avec Odoo 18
            # 'parc_IT/static/src/js/portal.js',
            'parc_IT/static/src/scss/portal.scss',
        ],
    }
} 
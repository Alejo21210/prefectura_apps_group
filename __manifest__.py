{
    'name': 'Sistema de Cajas EPS - Prefectura',
    'version': '19.0.1.0.0',
    'summary': 'Gestión Multi-Caja EPS con roles y parámetros',
    'description': """
        Sistema de Cajas de Ahorro de la Economía Popular y Solidaria (EPS)
        ======================================================================
        
        * Gestión de múltiples cajas de ahorro
        * Control de socios con indicadores sociales
        * Registro de aportes y créditos
        * Roles y permisos por caja
        * Reportes financieros y sociales
        
        GAD Prefectura de Pichincha - Proyecto MERA
    """,
    'author': 'Alejo - Prefectura de Pichincha',
    'website': 'https://www.pichincha.gob.ec',
    'category': 'Accounting/Finance',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/eps_security.xml',
        'security/ir.model.access.csv',
        'views/eps_caja_views.xml',
        'views/eps_socio_views.xml',
        'views/eps_socio_import_wizard_views.xml',
        'views/res_users_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
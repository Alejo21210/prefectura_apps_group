{
    'name': "Gestión de Cartera de Créditos - Prefectura UTE",

    'summary': "Control de cartera: créditos, cuotas, amortización y cartera vencida",

    'description': """
        Módulo completo para la gestión de cartera de créditos que incluye:
        * Creación de créditos con socios y garantes
        * Generación automática de tabla de amortización (método francés/alemán)
        * Registro de pagos con validaciones
        * Cálculo de cartera vencida por período
        * Alertas de pagos solo interés
        * Reportes e indicadores de cartera
    """,

    'author': "Prefectura UTE",
    'website': "https://www.yourcompany.com",

    'category': 'Accounting',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/cartera_security.xml',
        'security/ir.model.access.csv',
        'security/cartera_record_rules.xml',
        'views/cartera_credito_views.xml',
        'views/cartera_cuota_views.xml',
        'views/cartera_pago_views.xml',
        'views/cartera_menu.xml',
        'views/res_users_views.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}


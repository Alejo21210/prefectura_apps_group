{
    'name': "Libros Diarios EPS",
    'summary': "Registro de Ingresos y Egresos",
    'description': """
        Módulo para la gestión operativa diaria de la Caja EPS:
        - Registro de Egresos Operativos y Desembolsos.
        - Control de Destino del Crédito (Sectores).
        - Generación de Comprobantes PDF.
    """,
    'author': "Yandri",
    'category': 'Accounting',
    'version': '1.0',
    'depends': ['base', 'mail', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/eps_egreso_views.xml',
        'reports/eps_egreso_report.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

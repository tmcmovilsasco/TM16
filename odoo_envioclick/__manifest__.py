# -*- coding: utf-8 -*-
{
    'name': "Conector EnvioClick",
    'summary': """
        Conector API envioclickpro
        """,
    'description': """
        Integracíon con el modulo de ventas en odoo para determinar el costo del envío y crear la solicitud de envíos automatico, 
        generando la etiqueta y gestionando el segimiento en el modulo de inventario
        """,
    'author': 'Walter Falla Morales',
    'company': 'Intsyd SAS',
    'website': 'https://www.intsyd.com',
    'category': 'Inventory',
    "version": "16.0.1",
    "application": False,
    'depends': ['base', 'sale_management', 'stock', 'l10n_co_extra','contacts','base_address_extended'],
    'data': [
        'views/package_type.xml',
        'views/res_company.xml',
        'views/res_city.xml',
        'views/product_template.xml',
        'views/product_product.xml',
        'security/ir.model.access.csv',
        'views/sale_order.xml',
        'views/odoo_envioclick.xml',
        'views/quotation_envioclick.xml',
        'views/stock_picking.xml',
        'views/shipment_envioclick.xml',
        'views/res_partner.xml',
    ],
    "license": "OPL-1",
    'images': [
    ],
    "auto_install": False,
    "installable": True,
}

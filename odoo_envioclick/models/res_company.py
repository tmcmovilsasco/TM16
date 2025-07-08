from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    envioclick_endpoint = fields.Char(string="Endpoint", default="https://api.envioclickpro.com.co/api/v2")
    envioclick_api_key = fields.Char(string="API Key Authentication")

    default_package_description = fields.Char(string="Default Package Description")
    test_mode = fields.Boolean(string="Test mode", default=True)

    insurance = fields.Boolean(string="Secure Packages", default=True)
    requestPickup = fields.Boolean(string="Request Pickup", default=True)
    pickupDate = fields.Selection([
        ('same_day', 'Same Day'),
        ('next_day', 'Next Day'), ], string='Pickup Date', default='same_day')
    automate_shipment = fields.Boolean(string="Automate Shipment", default=True)

    origin_firstName = fields.Char(string="Nombre de la persona que envía")
    origin_lastName = fields.Char(string="Apellido de la persona que envía")

    promocion_activa = fields.Char(string="Promoción Activa")
    permitir_envio_promo = fields.Boolean(string="Generar Guías a promoción")
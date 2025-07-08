from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    billing_address_3 = fields.Char(string="Calle 3")
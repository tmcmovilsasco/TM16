from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    length = fields.Float(string="Length(cm)", digits='Volume')
    height = fields.Float(string="Height(cm)", digits='Volume')
    width = fields.Float(string="Width(cm)", digits='Volume')







# coding: utf-8

from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_scheme_id = fields.Many2one(
        comodel_name='product.scheme',
        string='Esquema de producto',
        default=lambda self: self.env['product.scheme'].search([('code', '=', '001')], limit=1))

    unspsc_product_id = fields.Many2one('unspsc.product', 'Producto UNSPSC',
        help='El código UNSPSC relacionado con este producto.')

    unspsc_class_id = fields.Many2one('unspsc.class', related="unspsc_product_id.class_id")
    unspsc_family_id = fields.Many2one('unspsc.family', related="unspsc_product_id.family_id")
    unspsc_segment_id = fields.Many2one('unspsc.segment', related="unspsc_product_id.segment_id")


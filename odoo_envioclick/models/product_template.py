from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    length = fields.Float(string="Length(cm)", digits='Volume', compute='_compute_length', inverse='_set_length', store=True)
    height = fields.Float(string="Height(cm)", digits='Volume', compute='_compute_height', inverse='_set_height', store=True)
    width = fields.Float(string="Width(cm)", digits='Volume', compute='_compute_width', inverse='_set_width', store=True)

    @api.depends('product_variant_ids', 'product_variant_ids.length')
    def _compute_length(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.length = template.product_variant_ids.length
        for template in (self - unique_variants):
            template.length = 0.0

    def _set_length(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.length = template.length

    @api.depends('product_variant_ids', 'product_variant_ids.height')
    def _compute_height(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.height = template.product_variant_ids.height
        for template in (self - unique_variants):
            template.height = 0.0

    def _set_height(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.height = template.height

    @api.depends('product_variant_ids', 'product_variant_ids.width')
    def _compute_width(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.width = template.product_variant_ids.width
        for template in (self - unique_variants):
            template.width = 0.0

    def _set_width(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.width = template.width







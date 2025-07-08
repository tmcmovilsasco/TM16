# -*- coding: utf-8 -*-

from odoo import fields, models

class ProductUom(models.Model):
	_inherit = 'uom.uom'

	product_uom_code_id = fields.Many2one(
		comodel_name='product.uom.code',
		string='Código de unidad de medida')

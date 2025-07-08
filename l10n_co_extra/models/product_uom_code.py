# -*- coding: utf-8 -*-

from odoo import fields, models

class ProductUomCode(models.Model):
	_name = 'product.uom.code'

	name = fields.Char(string='Nombre')
	code = fields.Char(string='Código')

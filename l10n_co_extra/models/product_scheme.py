# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductScheme(models.Model):
    _name = 'product.scheme'

    code = fields.Char(string='ID Esquema')
    name = fields.Char(string='Nombre del Esquema')
    scheme_agency_id = fields.Char(string='ID Esquema Agencia')

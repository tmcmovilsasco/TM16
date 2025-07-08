# coding: utf-8

from odoo import fields, models


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    codigo_departamento = fields.Integer("Código departamento")

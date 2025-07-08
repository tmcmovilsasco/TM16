# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResBank(models.Model):
    _inherit = 'res.bank'

    zip_id = fields.Many2one("res.city.zip", "Código postal")
    city_id = fields.Many2one('res.city', string='Ciudad', ondelete='restrict', required=False)

    @api.onchange("zip_id")
    def _onchange_zip_id(self):
        if self.zip_id:
            vals = {
                "city_id": self.zip_id.city_id,
                "zip": self.zip_id.name,
                "city": self.zip_id.city_id.name,
            }
            if self.zip_id.city_id.country_id:
                vals.update({"country": self.zip_id.city_id.country_id})
            if self.zip_id.city_id.state_id:
                vals.update({"state": self.zip_id.city_id.state_id})
            self.update(vals)
        else:
            vals = {
                "city_id": False,
                "zip": '',
                "city": '',
            }
            self.update(vals)
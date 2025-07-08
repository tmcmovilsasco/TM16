# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    city_id = fields.Many2one(
        "res.city",
        string="Ciudad",
    )
    zip_id = fields.Many2one(
        "res.city.zip",
        string="Código postal",
    )

    country_enforce_cities = fields.Boolean(
        related="partner_id.country_id.enforce_cities"
    )

    def _get_company_address_fields(self, partner):
        res = super()._get_company_address_fields(partner)
        res["city_id"] = partner.city_id
        res["zip_id"] = partner.zip_id
        return res

    # def _inverse_city_id(self):
    #     for company in self:
    #         company.with_context(
    #             skip_check_zip=True
    #         ).partner_id.city_id = company.city_id
    #
    # def _inverse_zip_id(self):
    #     for company in self:
    #         company.with_context(skip_check_zip=True).partner_id.zip_id = company.zip_id
    #
    # def _inverse_state(self):
    #     return super(
    #         ResCompany, self.with_context(skip_check_zip=True)
    #     )._inverse_state()
    #
    # def _inverse_country(self):
    #     return super(
    #         ResCompany, self.with_context(skip_check_zip=True)
    #     )._inverse_country()

    @api.onchange("zip_id")
    def _onchange_zip_id(self):
        if self.zip_id:
            self.update(
                {
                    "zip": self.zip_id.name,
                    "city_id": self.zip_id.city_id,
                    "city": self.zip_id.city_id.name,
                    "country_id": self.zip_id.city_id.country_id,
                    "state_id": self.zip_id.city_id.state_id,
                }
            )

    @api.onchange("state_id")
    def _onchange_state_id(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id.id
# coding: utf-8

from odoo import api, fields, models
from os import path
import pandas as pd
import logging
_logger = logging.getLogger(__name__)

class ResCityZip(models.Model):
    _name = "res.city.zip"
    _order = "name asc"
    _rec_name = "display_name"

    name = fields.Char("ZIP", required=True)
    city_id = fields.Many2one("res.city", "Ciudad", required=True)
    display_name = fields.Char(
        compute="_compute_new_display_name", store=True, index=True
    )
    tipo = fields.Selection([("urbano", "Urbano"),
                                ("rural", "Rural")], string="Tipo", default='urbano')
    _sql_constraints = [
        (
            "name_city_uniq",
            "UNIQUE(name, city_id, tipo)",
            "You already have a zip with that code in the same city. "
            "The zip code must be unique within it's city",
        )
    ]

    @api.depends("name", "city_id")
    def _compute_new_display_name(self):
        for rec in self:
            name = [rec.name + '-' + rec.tipo.capitalize(), rec.city_id.name]
            if rec.city_id.state_id:
                name.append(rec.city_id.state_id.name)
            rec.display_name = ", ".join(name)

    @api.model
    def _load_zips_dian(self):
        _logger.info("Cargando códigos postales Colombia.")
        base_path = path.dirname(path.dirname(__file__))
        data = pd.read_excel(r'%sCodigos_Postales.xlsx' % (base_path + '/data/'))
        df = pd.DataFrame(data)
        cantidad = 0
        for row in df.itertuples():
            codigo_municipio = str(df.at[row.Index, 'codigo_municipio'])
            codigo_postal = str(df.at[row.Index, 'codigo_postal'])
            tipo = str(df.at[row.Index, 'tipo'])
            city = self.env['res.city'].search([('codigo_municipio', '=', int(codigo_municipio))])
            if city:
                self.create({
                    'name': codigo_postal,
                    'city_id': city.id,
                    'tipo': tipo.lower()
                })
                cantidad += 1
        _logger.info("%d códigos postales instalados.", cantidad)


from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.city'

    allow_envioclick = fields.Boolean(string="Allow EnvioClick", default=True)
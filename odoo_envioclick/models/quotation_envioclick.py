from odoo import api, models, fields

class QuotationEnvioClick(models.Model):
    _name = 'odoo_envioclick.quotation'
    _description = 'Cotizaciones de EnvioClick'

    sale_id = fields.Many2one('sale.order')
    partner_id = fields.Many2one('res.partner')
    idRate = fields.Integer(string="ID Rate")
    idProduct = fields.Integer(string="ID Product")
    product = fields.Char(string="Product")
    idCarrier = fields.Integer(string="ID Carrier")
    carrier = fields.Char(string="Carrier")
    flete = fields.Float(string="Flete")
    minimumInsurance = fields.Float(string="Minimum Insurance")
    extraInsurance = fields.Float(string="Extra Insurance")

    length = fields.Float(string="Length(cm)", digits='Volume')
    height = fields.Float(string="Height(cm)", digits='Volume')
    width = fields.Float(string="Width(cm)", digits='Volume')
    weight = fields.Float(string="Weight(kg)", digits='Volume')

    origin_daneCode = fields.Char(string="Origin daneCode")
    origin_address = fields.Char(string="Origin address")

    destination_daneCode = fields.Char(string="Destination daneCode")
    destination_address = fields.Char(string="Destination address")

    contentValue = fields.Float(string="Content Value")

    state = fields.Selection([
        ('waiting', 'Waiting'),
        ('accepted', 'Accepted'),
        ('canceled', 'Canceled'), ], string='State', default='waiting')

    packages = fields.Many2one('odoo_envioclick.package_type', string='Packages', related='sale_id.packages')

    company_id = fields.Many2one('res.company', related="sale_id.company_id")

    def name_get(self):
        result = []
        for record in self:
            name = (record.carrier if record.carrier else 'Woo') + '-' + record.product+': '+str(record.flete)
            result.append((record.id, name))
        return result


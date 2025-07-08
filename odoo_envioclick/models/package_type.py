from odoo import api, models, fields


class PackageType(models.Model):
    _name = 'odoo_envioclick.package_type'
    _description = 'Tipos de paquetes'
    _sql_constraints = [
        ('length_maximo', 'CHECK (length<=300)', 'La Longitud debe ser menor o igual a 300 cm.'),
        ('height_maximo', 'CHECK (height<=300)', 'La Altura debe ser menor o igual a 300 cm.'),
        ('width_maximo', 'CHECK (width<=300)', 'La Anchura debe ser menor o igual a 300 cm.')
    ]

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    description = fields.Char(string="Description")
    length = fields.Float(string="Length(cm)", digits='Volume', required=True)
    height = fields.Float(string="Height(cm)", digits='Volume', required=True)
    width = fields.Float(string="Width(cm)", digits='Volume', required=True)

    product_max = fields.Integer(string="Quantity of products")
    capacity = fields.Float(string="Capacity(kg)")

    weight_box = fields.Float(string="Width Box(kg)", digits='Volume', required=True)

    volume = fields.Float(string="Volume(cm)", compute="_volume", digits='Volume', store=True)
    active = fields.Boolean(string="Active", default=True)

    @api.depends('length', 'height', 'width')
    def _volume(self):
        for rec in self:
            if rec.length > 0 and rec.height >0 and rec.width>0:
                rec.volume = rec.length * rec.height * rec.width
            else:
                rec.volume = 0.0

    def name_get(self):
        result = []
        for record in self:
            name = record.code + '-' + record.name
            result.append((record.id, name))
        return result
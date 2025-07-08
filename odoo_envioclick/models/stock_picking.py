from odoo import models, fields, api
import qrcode
import base64

from io import BytesIO
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    shipment_envioclick = fields.Many2one('odoo_envioclick.shipment', string='Shipment')

    packages = fields.Many2one('odoo_envioclick.package_type', string='Packages', related='shipment_envioclick.packages')

    url_envioclick = fields.Char(string="URL etiqueta en PDF", related='shipment_envioclick.url')

    length = fields.Float(string="Length(cm)", digits='Volume', related='shipment_envioclick.length')
    height = fields.Float(string="Height(cm)", digits='Volume', related='shipment_envioclick.height')
    width = fields.Float(string="Width(cm)", digits='Volume', related='shipment_envioclick.width')
    weight = fields.Float(string="Weight(kg)", digits='Volume', related='shipment_envioclick.weight')

    qr_url = fields.Binary("QR Url")

    state_envio = fields.Selection([
        ('draft', '-'),
        ('gratis', 'Gratis'), ('envioclick', 'EnvioClick Generada'), ('envioclick_espera', 'Esperar EnvioClick')
    ], string='Estatus EnvioClick', copy=False, default='draft')

    def _get_qr_url(self):
        for rec in self:
            if rec.url_envioclick:
                rec.qr_url = self.generate_qr_code(rec.url_envioclick)

    def generate_qr_code(self, url):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_img = base64.b64encode(temp.getvalue())
        print(qr_img)
        return qr_img
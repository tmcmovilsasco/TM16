import requests
from odoo import api, models, fields,_
import base64#file encode
import logging
import json
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class ShipmentEnvioClick(models.Model):
    _name = 'odoo_envioclick.shipment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Guías de EnvioClick'

    sale_id = fields.Many2one('sale.order')
    partner_id = fields.Many2one('res.partner', store=True)
    idRate = fields.Integer(string="ID Rate")
    myShipmentReference = fields.Char(string="My Shipment Reference")
    requestPickup = fields.Boolean(string="Request Pickup")
    insurance = fields.Boolean(string="Insurance")
    description = fields.Char(string="Description")
    contentValue = fields.Float(string="Content Value")

    length = fields.Float(string="Length(cm)", digits='Volume')
    height = fields.Float(string="Height(cm)", digits='Volume')
    width = fields.Float(string="Width(cm)", digits='Volume')
    weight = fields.Float(string="Weight(kg)", digits='Volume')

    origin_company = fields.Char(string="Origin company")
    origin_firstName = fields.Char(string="Origin firstName")
    origin_lastName = fields.Char(string="Origin lastName")
    origin_email = fields.Char(string="Origin email")
    origin_phone = fields.Char(string="Origin phone")
    origin_address = fields.Char(string="Origin address")
    origin_crossStreet = fields.Char(string="Origin cross street")
    origin_reference = fields.Char(string="Origin reference")
    origin_suburb = fields.Char(string="Origin suburb")
    origin_daneCode = fields.Char(string="Origin daneCode")

    destination_company = fields.Char(string="Destination company")
    destination_firstName = fields.Char(string="Destination firstName")
    destination_lastName = fields.Char(string="Destination lastName")
    destination_email = fields.Char(string="Destination email")
    destination_phone = fields.Char(string="Destination phone")
    destination_daneCode = fields.Char(string="Destination daneCode")
    destination_crossStreet = fields.Char(string="Destination cross street")
    destination_reference = fields.Char(string="Destination reference")
    destination_suburb = fields.Char(string="Destination suburb")
    destination_address = fields.Char(string="Destination address")

    guide = fields.Char(string="Guide")
    guide_img = fields.Binary(string="Guide Image")
    url = fields.Char(string="URL etiqueta en PDF")
    tracker = fields.Char(string="Número para rastrear guía")
    idOrder = fields.Integer(string="Order EnvioClick")
    quotation_id = fields.Many2one('odoo_envioclick.quotation', string="Quotation EnvioClick")

    carrier = fields.Char(string="Carrier")
    flete = fields.Float(string="Flete", related='quotation_id.flete', store=True)

    guide_pdf = fields.Binary(string="Guide PDF", attachment=True)

    state = fields.Selection([
        ('pendiente_recoleccion', 'Pendiente Recolección'),
        ('en_ruta_a_recoleccion', 'En ruta a recolección'),
        ('en_transito', 'En tránsito'),
        ('en_ruta_de_entrega_final', 'En ruta de entrega final'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),], string='State Document', default='pendiente_recoleccion', tracking=True)
    status = fields.Char(string="Status EnvioClick", tracking=True)
    statusDetail = fields.Char(string="Status Detail", tracking=True)
    arrivalDate = fields.Datetime(string="Arrival Date", tracking=True)
    realPickupDate = fields.Datetime(string="Pickup Date", tracking=True)
    realDeliveryDate = fields.Datetime(string="Delivery Date", tracking=True)

    company_id = fields.Many2one('res.company', required=True, related="sale_id.company_id")

    packages = fields.Many2one('odoo_envioclick.package_type', string='Packages', related='sale_id.packages')

    def name_get(self):
        result = []
        for record in self:
            name = record.carrier + ' - Guía: ' + record.tracker
            result.append((record.id, name))
        return result

    def _get_image(self):
        for rec in self:
            rec.guide_img = base64.b64encode(rec.guide.encode('utf-8'))

    def track(self):
        for rec in self:
            url = rec.company_id.envioclick_endpoint + "/track"
            headers = {
                'AuthorizationKey': rec.company_id.envioclick_api_key,
                'Content-Type': 'application/json'
            }
            payload = {
                "trackingCode": rec.tracker
            }
            response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
            if response.text:
                response_json = json.loads(response.text)
                status_codes = response_json['status_codes'][0]
                print(response_json)
                if int(status_codes) == 200:
                    state = 'pendiente_recoleccion'
                    if 'status' in response_json['data']:
                        if 'Pendiente Recolección' in response_json['data']['status']:
                            state = 'pendiente_recoleccion'
                        elif 'En ruta a recolección' in response_json['data']['status']:
                            state = 'en_ruta_a_recoleccion'
                        elif 'En tránsito' in response_json['data']['status']:
                            state = 'en_transito'
                        elif 'Entregado' in response_json['data']['status']:
                            state = 'entregado'
                        elif 'Cancelado' in response_json['data']['status']:
                            state = 'cancelado'
                        status = response_json['data']['status']
                        statusDetail = response_json['data']['statusDetail']
                        rec.update({'state':state, 'status':status, 'statusDetail':statusDetail})
                    if 'error' in response_json['data']:
                        status_messages = response_json['data']['error']
                        raise UserError(str(status_messages))
                else:
                    status_messages = response_json['status_messages']['error']
                    raise UserError(str(status_messages))
            else:
                raise UserError(_('¡No hay respuesta de EnvioClick!'))

    def descargar_pdf(self):
        for rec in self:
            if rec.url:
                rec.update({'guide_pdf': self.fetch_pdf_from_url(rec.url) })

    def fetch_pdf_from_url(self, url):
        data = ''
        try:
            data = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
        except Exception as e:
            _logger.warning('There was a problem requesting the image from URL %s' % url)
            logging.exception(e)

        return data
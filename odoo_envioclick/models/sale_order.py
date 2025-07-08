from odoo import api, models, fields, _
import requests
from odoo.exceptions import UserError
import json
from datetime import datetime, date, timedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.depends("quotation_envioclick")
    def _compute_amount_shipment(self):
        for record in self:
            amount=0
            if record.quotation_envioclick:
                amount = record.quotation_envioclick.flete
            record.amount_shipment = amount
            
    state_envioclick = fields.Selection([
        ('without_quotation', 'Without Quotation'),
        ('quotation', 'Quotation'),
        ('shipment', 'Shipment'), ], string='State Envioclick', default='without_quotation', required=True, copy=False)

    packages = fields.Many2one('odoo_envioclick.package_type', string='Packages')

    length_packages_total = fields.Float(string="Length", digits='Volume')
    height_packages_total = fields.Float(string="Height", digits='Volume')
    width_packages_total = fields.Float(string="Width", digits='Volume')

    weight_products_total = fields.Float(string="Weight(kg)", digits='Volume', store=True, compute='_weight_products_total')

    quotation_envioclick = fields.Many2one('odoo_envioclick.quotation', string='Quotation', copy=False)

    shipment_envioclick = fields.Many2one('odoo_envioclick.shipment', string='Shipment', copy=False)

    amount_shipment = fields.Float(string="Amount Shipment", digits='Volume', copy=False, compute="_compute_amount_shipment")

    url_envioclick = fields.Char(string="URL etiqueta en PDF", related="shipment_envioclick.url", copy=False)

    city_id_shiping = fields.Many2one('res.city', string='City partner shipping',related="partner_shipping_id.city_id")

    allow_envioclick = fields.Boolean(string="Allow EnvioClick", related="city_id_shiping.allow_envioclick")

    promocion_woo = fields.Char(string="Promoción Woo")

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for so in self:
            if so.company_id.automate_shipment == True:
                if not so.shipment_envioclick:
                    if so.quotation_envioclick:
                        self.button_generate_shipment()
                #if so.woocommerce_order_id.state_envio == 'gratis':
                #    for picking in so.picking_ids:
                #      picking.state_envio = 'gratis'

        return res

    @api.depends('order_line','sale_order_template_id')
    def _weight_products_total(self):
        for rec in self:
            weight_total = 0
            volume_total = 0
            total_productos_cantidad = 0
            for l in rec.order_line:
                if l.product_id.type in ['product', 'consu']:
                    total_productos_cantidad = total_productos_cantidad + l.product_uom_qty
                    weight_total = weight_total + (l.product_uom_qty * l.product_id.weight)
                    volume_total = (l.product_id.length * l.product_id.height * l.product_id.width) * l.product_uom_qty + volume_total
            if volume_total > 0:
                packages = self.env['odoo_envioclick.package_type'].search([('volume', '>=', volume_total),('product_max', '>=', total_productos_cantidad),('capacity','>=',weight_total)], order="volume asc", limit=1)
                if weight_total > 1000:
                    raise UserError(_('¡El peso mámixo debe ser 1000kg!'))
                else:
                    if len(packages) > 0:
                        weight_total = weight_total + (packages.weight_box)

                    if weight_total < 1:
                        weight_total = 1

                    if len(packages) > 0:
                        rec.write({
                            'weight_products_total': weight_total,
                            'packages': packages.id,
                            'length_packages_total': packages.length,
                            'height_packages_total': packages.height,
                            'width_packages_total': packages.width,
                            'state_envioclick': 'without_quotation'
                        })
                    else:
                        rec.write({
                            'weight_products_total': weight_total,
                            'packages': False,
                            'length_packages_total': 0,
                            'height_packages_total': 0,
                            'width_packages_total': 0,
                            'state_envioclick': 'without_quotation'
                        })
            else:

                rec.write({
                    'weight_products_total': weight_total,
                    'packages': False,
                    'length_packages_total': 0,
                    'height_packages_total': 0,
                    'width_packages_total': 0,
                    'state_envioclick': 'without_quotation'
                })

    @api.onchange('packages')
    def _packages_onchange(self):
        for rec in self:
            if rec.packages:
                weight_total = 0
                for l in rec.order_line:
                    if l.product_id.type in ['product', 'consu']:
                        weight_total = weight_total + (l.product_uom_qty * l.product_id.weight)
                weight_total = weight_total + (rec.packages.weight_box)
                if weight_total < 1:
                    weight_total = 1
                rec.write({'length_packages_total': rec.packages.length,
                           'height_packages_total': rec.packages.height,
                           'width_packages_total': rec.packages.width,
                           'weight_products_total': weight_total,
                           'state_envioclick': 'without_quotation'
                           })
            else:
                rec.write({'length_packages_total': 0,
                           'height_packages_total': 0,
                           'width_packages_total': 0,
                           'state_envioclick': 'without_quotation'
                           })

    def button_get_quotation(self):
        for rec in self:

            quotation_old = self.env['odoo_envioclick.quotation'].search([('sale_id', '=', rec.id)])
            if len(quotation_old) > 0:
                for q in quotation_old:
                    q.unlink()

            if not rec.company_id.envioclick_api_key:
                raise UserError(_('¡Debe configurar el API KEY de EnvioClick!'))

            if not rec.packages:
                raise UserError(_('¡No hay una caja asignada a este pedido, verifique la configuración de las Cajas!'))
            if rec.weight_products_total == 0:
                raise UserError(
                    _('¡El peso de los productos no puede ser 0, verifique las dimenciones y peso de los productos!'))
            url = rec.company_id.envioclick_endpoint + "/quotation"
            headers = {
                'AuthorizationKey': rec.company_id.envioclick_api_key,
                'Content-Type': 'application/json'
            }
            origin_zip = rec.company_id.partner_id.city_id.zipcode
            origin_address = rec.company_id.partner_id.street
            destination_zip = rec.partner_shipping_id.city_id.zipcode
            destination_address = rec.partner_shipping_id.street

            if not rec.partner_id.email:
                raise UserError(_('¡El cliente debe tener registrado un email!'))

            if not rec.partner_shipping_id.phone:
                raise UserError(_('¡El cliente debe tener registrado un número de teléfono!'))

            if len(destination_address) > 50:
                destination_address = destination_address[:50]

            if rec.warehouse_id:
                if rec.warehouse_id.partner_id:
                    if rec.warehouse_id.partner_id.city_id:
                        origin_zip = rec.warehouse_id.partner_id.city_id.zipcode

            if rec.company_id.partner_id.country_id:
                if rec.company_id.partner_id.country_id.code == 'CO':
                    origin_zip = origin_zip + '000'
                    destination_zip = destination_zip + '000'

            payload = {
                "packages": [
                    {
                        "weight": rec.weight_products_total,
                        "height": rec.height_packages_total,
                        "width": rec.width_packages_total,
                        "length": rec.length_packages_total
                    }
                ],
                "description": rec.company_id.default_package_description,
                "contentValue": rec.amount_total,
                "origin": {
                    "daneCode": origin_zip,
                    "address": origin_address
                },
                "destination": {
                    "daneCode": destination_zip,
                    "address": (destination_address if len(destination_address)<51 else destination_address[:50])
                }
            }
            #print(json.dumps(payload))
            response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
            if response.text:
                response_json = json.loads(response.text)
                #print(response_json)
                status_codes = response_json['status_codes'][0]
                # print(status_codes)
                if int(status_codes) == 200:
                    # print(response_json)
                    lower_quotation = 0
                    lower_quotation_id = 0
                    for rates in response_json['data']['rates']:
                        quotation = {
                            'sale_id': rec.id,
                            'partner_id': rec.partner_id.id,
                            'idRate': rates['idRate'],
                            'idProduct': rates['idProduct'],
                            'product': rates['product'],
                            'idCarrier': rates['idCarrier'],
                            'contentValue': rec.amount_total,
                            'carrier': rates['carrier'],
                            'flete': rates['flete'],
                            'minimumInsurance': rates['minimumInsurance'],
                            'weight': rec.weight_products_total,
                            'height': rec.height_packages_total,
                            'width': rec.width_packages_total,
                            'length': rec.length_packages_total,
                            'origin_daneCode': origin_zip,
                            'origin_address': origin_address,
                            'destination_daneCode': destination_zip,
                            'destination_address': destination_address
                        }

                        quotation_id = self.env['odoo_envioclick.quotation'].create(quotation)
                        if quotation_id:
                            if lower_quotation == 0:
                                lower_quotation = quotation_id.flete
                                lower_quotation_id = quotation_id.id

                            if quotation_id.flete < quotation_id.flete:
                                lower_quotation = quotation_id.flete
                                lower_quotation_id = quotation_id.id

                    if lower_quotation > 0:
                        rec.write({'state_envioclick': 'quotation', 'quotation_envioclick': lower_quotation_id})
                    else:
                        raise UserError(_('¡No se recibió ninguna cotización!'))
                else:
                    status_messages = response_json['status_messages']['error']
                    raise UserError(str(status_messages))
            else:
                raise UserError(_('¡No hay respuesta de EnvioClick!'))

    def button_generate_shipment(self):
        for rec in self:
            #verificar si tiene promocion restringida
            if rec.promocion_woo:
                if rec.promocion_woo == rec.company_id.promocion_activa and not rec.company_id.permitir_envio_promo:
                    #no genera guia
                    for picking in rec.picking_ids:
                        picking.state_envio = 'envioclick_espera'
                    continue

            if rec.quotation_envioclick:
                url = rec.company_id.envioclick_endpoint + "/shipment"
                headers = {
                    'AuthorizationKey': rec.company_id.envioclick_api_key,
                    'Content-Type': 'application/json'
                }
                if rec.company_id.test_mode:
                    url = rec.company_id.envioclick_endpoint + "/shipment_sandbox"

                pickupDate = fields.Datetime.now()
                #if rec.company_id.pickupDate == 'next_day':
                #    tomorrow = fields.Datetime.now() + timedelta(days=1)
                #    pickupDate = tomorrow.strftime('%Y-%m-%d')
                día_semana = fields.Datetime.now().weekday()
                if día_semana < 5:
                    print("entre semana")
                else:  # 5 Sat, 6 Sun
                    if día_semana == 5:
                        pickupDate = fields.Datetime.now() + timedelta(days=2)
                    else:
                        pickupDate = fields.Datetime.now() + timedelta(days=1)
                origin_email = rec.company_id.partner_id.email
                origin_suburb = rec.company_id.partner_id.street
                origin_phone = rec.company_id.partner_id.phone

                if not rec.partner_id.email:
                    raise UserError(_('¡El cliente debe tener registrado un email!'))

                if not rec.partner_shipping_id.phone:
                    raise UserError(_('¡El cliente debe tener registrado un número de teléfono!'))

                if rec.warehouse_id:
                    if rec.warehouse_id.partner_id:
                        if rec.warehouse_id.partner_id.zip:
                            origin_email = rec.warehouse_id.partner_id.email
                            origin_suburb = rec.warehouse_id.partner_id.street
                            origin_phone = rec.warehouse_id.partner_id.phone

                if len(origin_phone) > 10:
                    origin_phone = origin_phone[:10]

                destination_company = rec.partner_shipping_id.name
                destination_firstName = 'N/A'
                destination_lastName = 'N/A'

                # solo para el caso de la pocion tomar los nombres desde el partner principal
                if rec.partner_id.company_type == 'person' and rec.partner_id.person_type == '2':
                    destination_company = 'N/A'
                    destination_firstName = rec.partner_id.firstname
                    if rec.partner_id.other_name:
                        destination_firstName = destination_firstName + ' ' + rec.partner_id.other_name
                    destination_lastName = rec.partner_id.lastname
                    if rec.partner_id.other_lastname:
                        destination_lastName = destination_lastName + ' ' + rec.partner_id.other_lastname

                if len(destination_company) > 28:
                    destination_company = destination_company[:28]

                if len(destination_firstName) > 14:
                    destination_firstName = destination_firstName[:14]

                if len(destination_lastName) > 14:
                    destination_lastName = destination_lastName[:14]
                destination_suburb = (rec.partner_shipping_id.billing_address_3 if rec.partner_shipping_id.billing_address_3 else '--')
                if len(destination_suburb) > 30:
                    destination_suburb = destination_suburb[:30]

                destination_reference = (rec.partner_shipping_id.street2 if rec.partner_shipping_id.street2 else '--')
                if len(destination_reference) > 25:
                    destination_reference = destination_reference[:25]


                #tmporal
                origin_zip = rec.quotation_envioclick.origin_daneCode
                phone_destination = rec.partner_id.phone
                if '+57' in phone_destination:
                    phone_destination = phone_destination.replace('+57', '')
                payload = {
                    "idRate": rec.quotation_envioclick.idRate,
                    "myShipmentReference": "Orden " + rec.name,
                    "requestPickup": rec.company_id.requestPickup,
                    "pickupDate": pickupDate.strftime('%Y-%m-%d'),
                    "insurance": rec.company_id.insurance,
                    "description": rec.company_id.default_package_description,
                    "contentValue": rec.quotation_envioclick.contentValue,
                    "packages": [
                        {
                            "weight": rec.quotation_envioclick.weight,
                            "height": rec.quotation_envioclick.height,
                            "width": rec.quotation_envioclick.width,
                            "length": rec.quotation_envioclick.length
                        }
                    ],
                    "origin": {
                        "company": rec.company_id.name,
                        "firstName": rec.company_id.origin_firstName,
                        "lastName": rec.company_id.origin_lastName,
                        "email": origin_email,
                        "phone": origin_phone,
                        "address": rec.company_id.street,
                        "suburb": origin_suburb,
                        "crossStreet": "N/A",
                        "reference": "N/A",
                        "daneCode": origin_zip,
                    },
                    "destination": {
                        "company": destination_company,
                        "firstName": destination_firstName,
                        "lastName": destination_lastName,
                        "email": (rec.partner_id.email if len(rec.partner_id.email) < 61 else rec.partner_id.email[:60]),
                        "phone": phone_destination,
                        "address": rec.quotation_envioclick.destination_address,
                        "suburb": destination_suburb,
                        "crossStreet": (rec.partner_shipping_id.city_id.name if rec.partner_shipping_id.city_id else 'N/A'),
                        "reference": destination_reference,
                        "daneCode": rec.quotation_envioclick.destination_daneCode
                    }
                }
                #print(json.dumps(payload))
                response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
                # print(response)
                # print(response.text)
                if response.text:
                    response_json = json.loads(response.text)
                    #print(response_json)
                    status_codes = response_json['status_codes'][0]
                    if int(status_codes) == 200:
                        shipment = {
                            'sale_id': rec.id,
                            'partner_id': rec.partner_id.id,
                            'idRate': response_json['data']['idRate'],
                            'myShipmentReference': response_json['data']['myShipmentReference'],
                            'requestPickup': response_json['data']['requestPickup'],
                            'insurance': response_json['data']['insurance'],
                            'description': response_json['data']['description'],
                            'contentValue': response_json['data']['contentValue'],
                            'weight': response_json['data']['packages'][0]['weight'],
                            'height': response_json['data']['packages'][0]['height'],
                            'width': response_json['data']['packages'][0]['width'],
                            'length': response_json['data']['packages'][0]['length'],

                            'origin_company': response_json['data']['origin']['company'],
                            'origin_firstName': response_json['data']['origin']['firstName'],
                            'origin_lastName': response_json['data']['origin']['lastName'],
                            'origin_email': response_json['data']['origin']['email'],
                            'origin_phone': response_json['data']['origin']['phone'],
                            'origin_address': response_json['data']['origin']['address'],
                            'origin_crossStreet': response_json['data']['origin']['crossStreet'],
                            'origin_reference': response_json['data']['origin']['reference'],
                            'origin_suburb': response_json['data']['origin']['suburb'],
                            'origin_daneCode': response_json['data']['origin']['daneCode'],

                            'destination_company': response_json['data']['destination']['company'],
                            'destination_firstName': response_json['data']['destination']['firstName'],
                            'destination_lastName': response_json['data']['destination']['lastName'],
                            'destination_email': response_json['data']['destination']['email'],
                            'destination_phone': response_json['data']['destination']['phone'],
                            'destination_address': response_json['data']['destination']['address'],
                            'destination_crossStreet': response_json['data']['destination']['crossStreet'],
                            'destination_reference': response_json['data']['destination']['reference'],
                            'destination_suburb': response_json['data']['destination']['suburb'],
                            'destination_daneCode': response_json['data']['destination']['daneCode'],

                            'guide': response_json['data']['guide'],
                            'url': response_json['data']['url'],
                            'tracker': response_json['data']['tracker'],
                            'idOrder': response_json['data']['idOrder'],
                            'quotation_id': rec.quotation_envioclick.id,
                            'carrier': rec.quotation_envioclick.carrier
                        }
                        shipment_id = self.env['odoo_envioclick.shipment'].create(shipment)
                        if shipment_id:
                            quotation_ids = self.env['odoo_envioclick.quotation'].search(
                                [('sale_id', '=', shipment_id.sale_id.id)])
                            for q in quotation_ids:
                                if q == shipment_id.quotation_id:
                                    q.state = 'accepted'
                                else:
                                    q.state = 'canceled'
                            rec.write({'shipment_envioclick': shipment_id.id,
                                       'amount_shipment': rec.quotation_envioclick.flete,
                                       'amount_total': (rec.quotation_envioclick.flete + rec.amount_total),
                                       'state_envioclick': 'shipment'})

                            for picking in rec.picking_ids:
                                picking.shipment_envioclick = shipment_id
                                picking.state_envio = 'envioclick'
                                picking._get_qr_url()
                    else:
                        raise UserError(str(response_json))
                else:
                    raise UserError(_('¡No hay respuesta de EnvioClick!'))
            else:
                raise UserError(_('¡Debe seleccionar una cotización de EnvioClick!'))

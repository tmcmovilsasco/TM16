# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    name = fields.Char(
        compute="_compute_name",
        required=False,
        store=True,
        readonly=False, )

    firstname = fields.Char(string='Primer nombre')
    other_name = fields.Char(string='Segundo nombre')
    lastname = fields.Char(string='Primer apellido')
    other_lastname = fields.Char(string='Segundo apellido')

    person_type = fields.Selection([("1", "Persona Jurídica y asimiladas"),
                                    ("2", "Persona Natural y asimiladas")], string="Tipo de persona", default="2")

    vat_type = fields.Selection([
        ('11', u'11 - Registro civil'),
        ('12', u'12 - Tarjeta de identidad'),
        ('13', u'13 - Cédula de ciudadanía'),
        ('21', u'21 - Tarjeta de extranjería'),
        ('22', u'22 - Cédula de extranjería'),
        ('31', u'31 - NIT (Número de identificación tributaria)'),
        ('41', u'41 - Pasaporte'),
        ('42', u'42 - Documento de identificación extranjero'),
        ('47', u'47 - PEP'),
        ('50', u'50 - NIT de otro país'),
        ('91', u'91 - NUIP')
    ], string='Tipo de documento',
        help='''Identificador de cliente, según tipos dados por la DIAN.
                     Si es una persona física y tiene RUT use NIT''',
        required=True, default='13'
    )
    vat_vd = fields.Char('Dígito verificador', size=1, help='VD')

    zip_id = fields.Many2one("res.city.zip", "Código postal")
    city_id = fields.Many2one('res.city', string='Ciudad', ondelete='restrict', required=False)
    country_code = fields.Char(related='country_id.code', store=False)

    ciiu = fields.Many2many('ciiu', string='Clasificador CIIU')

    @api.model
    def create(self, vals):
        context = dict(self.env.context)
        name = vals.get("name", context.get("default_name"))
        if name is None:
            vals["name"] = " ".join(p for p in (vals["lastname"], vals["other_lastname"], vals["firstname"], vals["other_name"]) if p)
        return super(ResPartner, self.with_context(context)).create(vals)

    @api.onchange("person_type")
    def onchange_person_type(self):
        if self.person_type == "1":
            self.company_type = "company"
        elif self.person_type == "2":
            self.company_type = "person"

    @api.depends("firstname", "other_name", "lastname", "other_lastname")
    def _compute_name(self):
        for partner in self:
            partner.name = " ".join(p for p in (partner.lastname, partner.other_lastname, partner.firstname, partner.other_name) if p)

    @api.onchange("city_id")
    def _onchange_city_id(self):
        if not self.zip_id:
            super()._onchange_city_id()
        if self.zip_id and self.city_id != self.zip_id.city_id:
            self.update({"zip_id": False, "zip": False, "city": False})
        if self.city_id and self.country_enforce_cities:
            zip_principal = False
            if len(self.city_id.zip_ids)>0:
                zip_principal = self.city_id.zip_ids[0].name
                self.update({"zip": zip_principal, "zip_id":self.city_id.zip_ids[0].id})
            return {"domain": {"zip_id": [("city_id", "=", self.city_id.id)]}}
        return {"domain": {"zip_id": []}}

    @api.onchange("country_id")
    def _onchange_country_id(self):
        res = super()._onchange_country_id()
        if self.zip_id and self.zip_id.city_id.country_id != self.country_id:
            self.zip_id = False
        return res

    @api.onchange("zip_id")
    def _onchange_zip_id(self):
        if self.zip_id:
            vals = {
                "city_id": self.zip_id.city_id,
                "zip": self.zip_id.name,
                "city": self.zip_id.city_id.name,
            }
            if self.zip_id.city_id.country_id:
                vals.update({"country_id": self.zip_id.city_id.country_id})
            if self.zip_id.city_id.state_id:
                vals.update({"state_id": self.zip_id.city_id.state_id})
            self.update(vals)
        elif not self.country_enforce_cities:
            self.city_id = False

    @api.constrains("zip_id", "country_id", "city_id", "state_id")
    def _check_zip(self):
        if self.env.context.get("skip_check_zip"):
            return
        for rec in self:
            if not rec.zip_id:
                continue
            if rec.state_id and rec.zip_id.city_id.state_id != rec.state_id:
                raise ValidationError(
                    _("The state of the partner %s differs from that in " "location %s")
                    % (rec.name, rec.zip_id.name)
                )
            if rec.country_id and rec.zip_id.city_id.country_id != rec.country_id:
                raise ValidationError(
                    _(
                        "The country of the partner %s differs from that in "
                        "location %s"
                    )
                    % (rec.name, rec.zip_id.name)
                )
            if rec.city_id and rec.type != 'contact' and rec.zip_id.city_id != rec.city_id:
                raise ValidationError(
                    _("The city of partner %s differs from that in " "location %s")
                    % (rec.name, rec.zip_id.name)
                )

    @api.onchange("state_id")
    def _onchange_state_id(self):
        vals = {}
        if self.state_id.country_id:
            vals.update({"country_id": self.state_id.country_id})
        if self.zip_id and self.state_id != self.zip_id.city_id.state_id:
            vals.update({"zip_id": False, "zip": False, "city": False})
        self.update(vals)
        if self.state_id and not self.zip_id:
            cities_ids = self.env['res.city'].search([('state_id', '=', self.state_id.id)]).ids
            return {'domain': {'zip_id': [('city_id', 'in', cities_ids)],
                               'city_id': [('id', 'in', cities_ids)]}}

    @api.depends('vat_type')
    @api.onchange('vat')
    def _onchange_vat(self):
        for partner in self:
            if partner.vat_type == '31':
                if partner.vat == False:
                    partner.vat = ''
                else:
                    partner.vat_vd = self._check_dv(str(partner.vat))

    def _check_dv(self, nit):

        for item in self:
            if item.vat_type != '31':
                return str(nit)

            nitString = '0'*(15-len(nit)) + nit
            vl = list(nitString)
            result = (
                int(vl[0])*71 + int(vl[1])*67 + int(vl[2])*59 + int(vl[3])*53 +
                int(vl[4])*47 + int(vl[5])*43 + int(vl[6])*41 + int(vl[7])*37 +
                int(vl[8])*29 + int(vl[9])*23 + int(vl[10])*19 + int(vl[11])*17 +
                int(vl[12])*13 + int(vl[13])*7 + int(vl[14])*3
            ) % 11

            if result in (0, 1):
                return str(result)
            else:
                return str(11-result)

    @api.constrains('vat', 'vat_type', 'country_id')
    def check_vat(self):
        if self.env.context.get('company_id'):
            company = self.env['res.company'].browse(self.env.context['company_id'])
        else:
            company = self.env.company
        eu_countries = self.env.ref('base.europe').country_ids
        for partner in self:

            if not partner.vat:
                continue
            else:
                if partner.country_id:
                    vat_country = partner.country_id.code.lower()
                    if vat_country == 'co':
                        continue
                else:
                    continue

            #check with country code as prefix of the TIN
            vat_country, vat_number = self._split_vat(partner.vat)
            if company.vat_check_vies and partner.commercial_partner_id.country_id in eu_countries:
                # force full VIES online check
                check_func = self.vies_vat_check
            else:
                # quick and partial off-line checksum validation
                check_func = self.simple_vat_check
            if not check_func(vat_country, vat_number):
                #if fails, check with country code from country
                country_code = partner.commercial_partner_id.country_id.code
                if country_code:
                    if not check_func(country_code.lower(), partner.vat):
                        msg = partner._construct_constraint_msg(country_code.lower())
                        raise ValidationError(msg)
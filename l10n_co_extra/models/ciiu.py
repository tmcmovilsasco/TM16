# -*- coding: utf-8 -*-


from odoo import models, fields, api


class IndustrialClassification(models.Model):
    _name = "ciiu"  # res.co.ciiu
    _description = "ISIC List"

    name = fields.Char(
        string="Code and Description",
        store=True,
        compute="_compute_concat_name"
    )
    code = fields.Char('Code', required=True)
    description = fields.Char('Description', required=True)
    type = fields.Char(
        'Type',
        store=True,
        compute="_compute_set_type"
    )
    has_parent = fields.Boolean('Has Parent?')
    parent = fields.Many2one('ciiu', 'Parent')

    has_division = fields.Boolean('Has Division?')
    division = fields.Many2one('ciiu', 'Division')

    has_section = fields.Boolean('Has Section?')
    section = fields.Many2one('ciiu', 'Section')

    hierarchy = fields.Selection(
        [
            ("1", 'Has Parent?'),
            ("2", 'Has Division?'),
            ("3", 'Has Section?')
        ],
        'Hierarchy'
    )


    @api.depends('code', 'description')
    def _compute_concat_name(self):
        """
        This function concatinates two fields in order to be able to search
        for CIIU as number or string
        @return: void
        """
        for rec in self:
            if rec.code is False or rec.description is False:
                rec.name = ''
            else:
                rec.name = rec.code + ' - ' + rec.description
                #rec.name = str(rec.code.encode('utf-8').strip()) + \
                #    ' - ' + str(rec.description.encode('utf-8').strip())


    @api.depends('has_parent')
    def _compute_set_type(self):
        """
        Section, Division and Parent should be visually separated in the tree
        view. Therefore we tag them accordingly as 'view' or 'other'
        @return: void
        """
        for rec in self:
            # Child
            if rec.has_parent is True:
                if rec.division is True:
                    rec.type = 'view'
                elif rec.section is True:
                    rec.type = 'view'
                else:
                    rec.type = 'other'
            # Division
            else:
                rec.type = 'view'

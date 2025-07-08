# -*- coding: utf-8 -*-
from odoo import api, fields, models
from os import path
import pandas as pd
import logging
_logger = logging.getLogger(__name__)

class UNSPSCSegment(models.Model):
	_name = 'unspsc.segment'
	_description = 'Model Segmento UNSPSC'

	segment = fields.Char(string="Código de segmento UNSPSC", required=True)
	name = fields.Char(string="Nombre de segmento UNSPSC", required=True)

	def name_get(self):
		result = []
		for prod in self:
			result.append((prod.id, "%s %s" % (prod.segment, prod.name or '')))
		return result


class UNSPSCFamily(models.Model):
	_name = 'unspsc.family'
	_description = 'Model Familia UNSPSC'

	family = fields.Char(string="Código de familia UNSPSC", required=True)
	name = fields.Char(string="Nombre de familia UNSPSC", required=True)

	segment_id = fields.Many2one('unspsc.segment', string="Segmento UNSPSC")

	def name_get(self):
		result = []
		for prod in self:
			result.append((prod.id, "%s %s" % (prod.family, prod.name or '')))
		return result


class UNSPSCClass(models.Model):
	_name = 'unspsc.class'
	_description = 'Model clase UNSPSC'

	classe = fields.Char(string="Código de clase UNSPSC", required=True)
	name = fields.Char(string="Nombre de clase UNSPSC", required=True)
	family_id = fields.Many2one('unspsc.family', string="Familia UNSPSC")

	def name_get(self):
		result = []
		for prod in self:
			result.append((prod.id, "%s %s" % (prod.classe, prod.name or '')))
		return result


class UNSPSCProduct(models.Model):
	_name = 'unspsc.product'
	_description = 'Model producto UNSPSC'

	product = fields.Char(string="Código de producto UNSPSC", required=True)
	name = fields.Char(string="Nombre de producto UNSPSC", required=True)
	class_id =  fields.Many2one('unspsc.class', string="Clase UNSPSC")
	family_id = fields.Many2one('unspsc.family', related="class_id.family_id", string="Familia UNSPSC")
	segment_id = fields.Many2one('unspsc.segment', related="family_id.segment_id", string="Segmento UNSPSC")

	def name_get(self):
		result = []
		for prod in self:
			result.append((prod.id, "%s %s" % (prod.product, prod.name or '')))
		return result

	@api.model
	def _load_unspsc_product(self):
		_logger.info("Cargando Productos UNSPSC.")
		base_path = path.dirname(path.dirname(__file__))
		data = pd.read_excel(r'%sUNSPSC.xls' % (base_path + '/data/'))
		df = pd.DataFrame(data)
		cantidad = 0
		code = []
		fam = ''
		segmento = False
		segmento_id = False
		familia = False
		familia_id = False
		clase = False
		clase_id = False
		producto = False
		producto_id = False

		for row in df.itertuples():
			codigo_segmento = str(df.at[row.Index, 'codigo_segmento'])
			nombre_segmento = str(df.at[row.Index, 'nombre_segmento'])
			codigo_familia = str(df.at[row.Index, 'codigo_familia'])
			nombre_familia = str(df.at[row.Index, 'nombre_familia'])
			codigo_clase = str(df.at[row.Index, 'codigo_clase'])
			nombre_clase = str(df.at[row.Index, 'nombre_clase'])
			codigo_producto = str(df.at[row.Index, 'codigo_producto'])
			nombre_producto = str(df.at[row.Index, 'nombre_producto'])

			if not codigo_segmento == segmento:
				#creo el segmento
				segmento_id = self.env['unspsc.segment'].create({
					'segment': codigo_segmento,
					'name': nombre_segmento,
				})
				segmento = codigo_segmento

			if not codigo_familia == familia:
				#creo la familia
				familia_id = self.env['unspsc.family'].create({
					'family': codigo_familia,
					'name': nombre_familia,
					'segment_id': segmento_id.id
				})
				familia = codigo_familia

			if not codigo_clase == clase:
				#creo la clase
				clase_id = self.env['unspsc.class'].create({
					'classe': codigo_clase,
					'name': nombre_clase,
					'family_id': familia_id.id
				})
				clase = codigo_clase

			self.create({
				'product': codigo_producto,
				'name': nombre_producto,
				'class_id': clase_id.id
			})
			cantidad += 1

		_logger.info("%d Productos UNSPSC instalados.", cantidad)
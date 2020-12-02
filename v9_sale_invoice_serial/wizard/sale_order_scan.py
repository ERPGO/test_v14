# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import Warning


class sale_order_scan_wizard(models.TransientModel):
    _name = "sale.order.scan"
    _description = 'Sale Order Scan Wizard'

    scan = fields.Char(string="Scan")


    @api.onchange('scan')
    def add_product_via_scan_wizard(self):
        if self.scan:
            Product = self.env['stock.production.lot']
            order = self.env['sale.order'].browse(self._context.get('active_id'))
            products_ids = Product.search([('name', '=', self.scan)])
            if not products_ids:
                raise Warning(_(' %s Serial number is not available in system!!') % self.scan)

            line_list = []
            serial_no_list = []
            for product in products_ids:
                if not product.product_qty > 0.0 :
                    raise Warning(_('Stock not available with %s serial/lot number.') % self.scan)
                for line in order.order_line :
                    serial_no_list.append(line.serial_no.id)
                if product.id in serial_no_list :
                    self.scan = ''
                    raise Warning(_('This Serial Number/Lot Is Already In Sale Order Line!!'))
                else :
                    if product.product_qty > 0.0 :
                        vals = {
                        'order_id': order.id,
                        'product_id': product.product_id.id,
                        'name': product.product_id.name,
                        'product_uom_qty': product.product_qty,
                        'price_unit': product.product_id.product_tmpl_id.list_price,
                        'product_uom': product.product_id.product_tmpl_id.uom_id.id,
                        'state': 'draft',
                        'serial_no':product.id or False,
                        'tax_id': [(6, 0, product.product_id.taxes_id.ids)],
                                    }
                        #self.order_line.create(vals)
                        line_list.append((0, 0 , vals))
            order.write({'order_line' : line_list})
            self.scan = ''


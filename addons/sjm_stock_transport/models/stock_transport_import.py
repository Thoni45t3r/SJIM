# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2020  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Anggar Bagus Kurniawan <anggar.bagus@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero
from odoo.addons import decimal_precision as dp
import time
import os, base64, xlrd
import logging
_logger = logging.getLogger(__name__)

class StockTransportIMport(models.Model):
    _name = "stock.transport.import"
    _description = "Transport Import"

    date = fields.Date('Date', required=True)
    file = fields.Binary('File')
    file_name = fields.Char(required=False)
    import_line = fields.One2many('stock.transport.import.line', 'import_id', string='Import Lines', ondelete='cascade')
    state = fields.Selection([('draft','Draft'),('imported','Imported'),('confirmed','Confirmed')], string='State', default='draft')
    keterangan = fields.Text("Keterangan")
    product_spk_id = fields.Many2one('product.product', string='Product OA')
    # contract_id = fields.Many2one('weighbridge.contract', string="Kontrak")
    transport_move_ids = fields.Many2many('stock.transport.move', 'import_transport_move_rel', 'import_id', 'transport_move_id', string='Transport Moves')

    @api.multi
    def validate(self):
        warning = ''
        data = []
        for record in self:
            for line in record.import_line:
                # Contract
                wb_contract = self.env['weighbridge.contract'].search([('name','=',line.no_kontrak)], limit=1)
                if not wb_contract:
                    warning += "Kontrak '%s' tidak ada di sistem\n" % (line.no_kontrak)

                # Delivery
                wb_do = self.env['delivery.order.weighbridge'].search([('name', '=', line.no_do)], limit=1)
                if not wb_contract:
                    warning += "Delivery Order '%s' tidak ada di sistem\n" % (line.no_do)

                # Transporter
                transporter = self.env['res.partner'].search([('name','=',line.transporter)])
                if not transporter:
                    warning += "Transporter '%s' tidak ada di sistem\n" % (line.transporter)

                # Product
                # product = self.env['product.product'].search(['|',('default_code','=',line.product),('name','=',line.product)])
                product = self.env['product.product'].search([('default_code','=',line.product)], limit=1)
                # for x in product:
                    # print ">>>>>>>>>>>>>>>>>>>", x.name, x.default_code, x.id
                if not product:
                    warning += "Product '%s' tidak ada di sistem\n" % (line.product)

                # Source Location
                # if wb_do:
                #     src_location = wb_do.asal
                # else:
                src_location = self.env['stock.transport.location'].search([('name','=',line.src_location)])
                if not src_location:
                    warning += "Lokasi '%s' tidak ada di sistem\n" % (line.src_location)

                # Destination Location
                # if wb_do:
                #     dest_location = wb_do.tujuan
                # else:
                dest_location = self.env['stock.transport.location'].search([('name','=',line.dest_location)])
                
                if not dest_location:
                    warning += "Lokasi '%s' tidak ada di sistem\n" % (line.dest_location)

                # Rate Type
                list_rate_type = dict(self.env['stock.transport.move']._fields['rate_type'].selection)
                rate_type = {k:v for v, k in list_rate_type.items() if k == line.rate_type}
                if not rate_type:
                    warning += "Rate Type '%s' tidak ada dalam opsi" % (line.rate_type)
                else:
                    rate_type = rate_type[line.rate_type]

                if not warning:
                    rate = self.env['stock.transport.rate'].search([
                        ('partner_id', '=', transporter.id),
                        ('product_id', '=', product.id),
                        ('start_date', '<=', line.date),
                        ('end_date', '>=', line.date),
                        ('src_location_id', '=', src_location.id),
                        ('dest_location_id', '=', dest_location.id),
                        ('rate_type', '=', rate_type)
                        ])
                    if not rate:
                        warning += 'Rate Vendor %s, Product %s, Tanggal %s, Lokasi %s, Tujuan %s, Rate Type %s tidak ditemukan\n' % (
                            transporter.name, 
                            product.name,
                            line.date, 
                            src_location.name, dest_location.name, rate_type)
                    else:
                        if wb_contract.related_sale_id:
                            partner_order = wb_contract.related_sale_id.partner_id
                        elif wb_contract.related_purchase_id:
                            partner_order = wb_contract.related_purchase_id.partner_id
                        else:
                            partner_order = False
                        data.append({
                            'date' : line.date,
                            'no_tiket': line.no_tiket,
                            'no_plat': line.no_plat,
                            'driver_name': line.driver_name,
                            'relasi': line.relasi,
                            'contract_id': wb_contract.id,
                            'partner_order_id': partner_order.id if partner_order else False,
                            'wb_do': line.no_do,
                            'src_location' : src_location.id,
                            'src_bruto': line.src_bruto,
                            'src_tare': line.src_tare,
                            'src_netto': line.src_netto,
                            'dest_location' : dest_location.id,
                            'dest_bruto': line.dest_bruto,
                            'dest_tare': line.dest_tare,
                            'product_qty' : line.product_qty,
                            'transporter' : transporter.id,
                            'product' : product.id,
                            'rate_type' : rate_type,
                            'price_unit': rate.rate
                            })

            if not warning:
                created_ids = []
                for item in data:
                    transport_move = self.env['stock.transport.move'].create({
                        'date' : item.get('date',False),
                        'no_tiket': item.get('no_tiket'),
                        'no_plat': item.get('no_plat'),
                        'driver_name': item.get('driver_name'),
                        'relasi': item.get('relasi'),
                        'contract_id': item.get('contract_id',False),
                        'partner_order_id': item.get('partner_order_id',False),
                        'wb_do': item.get('wb_do'),
                        'src_location_id' : item.get('src_location',False),
                        'src_bruto': item.get('src_bruto',0.0),
                        'src_tare': item.get('src_tare',0.0),
                        'src_netto': item.get('src_netto',0.0),
                        'dest_location_id' : item.get('dest_location',False),
                        'dest_bruto': item.get('dest_bruto',0.0),
                        'dest_tare': item.get('dest_tare',0.0),
                        'product_qty' : item.get('product_qty',0.0),
                        'partner_id' : item.get('transporter',False),
                        'product_id' : item.get('product',False),
                        'product_spk_id': record.product_spk_id.id,
                        'rate_type' : item.get('rate_type',False),
                        'price_unit' : item.get('price_unit',False),
                        })
                    created_ids.append(transport_move.id)
                self.write({'state': 'confirmed','keterangan':False,
                    'transport_move_ids': [(6,0,created_ids)] if created_ids else []})
            else:
                self.write({'keterangan': warning})

    @api.multi
    def action_draft(self):
        for record in self:
            record.state='draft'
            record.file = False
            record.file_name = ''
            for x in record.import_line:
                x.unlink()

    @api.multi
    def import_transport(self):
        return self.upload_import_transport_function(False,False)

    @api.multi
    def upload_import_transport_function(self, workbook, sheet_number):
        data_matrix = {}

        if not workbook and not sheet_number:
            file = os.path.splitext(self.file_name)
            if file[1] not in ('.xls', '.xlsx'):
                raise UserError("Invalid File! Please import the correct file")

            wb = xlrd.open_workbook(file_contents=base64.decodestring(self.file))
            sheet = wb.sheet_by_index(0)
        else:
            wb = workbook
            sheet = wb.sheet_by_index(sheet_number)

        col = 1
        row = 1

        warning = ''

        # end of header section
        data_matrix = []
        # start validating detail section
        product_template_id = False
        while row != sheet.nrows:
            _logger.warning("row %s/%s" % (row,sheet.nrows))
            date = False
            no_tiket = ''
            no_plat = ''
            driver = ''
            relasi = ''
            kontrak = False
            delivery_order = False
            src_location = False
            src_bruto = False
            src_tare = False
            src_netto = False
            dest_location = False
            dest_bruto = False
            dest_tare = False
            product_qty = False
            transporter = False
            product = False
            keterangan = False
            rate_type = False

            # Tanggal
            col = 0
            # VALIDATE COLUMN
            if sheet.cell(row, col).value:
                if sheet.cell_type(row, col) != 3:
                    warning+="Data Kolom Tanggal pada baris ke %s bukan format tanggal\n" % (row)
                else:
                    date = datetime(*xlrd.xldate_as_tuple(sheet.cell(row, col).value, wb.datemode))
            else:
                warning+="Data Tanggal pada baris ke %s tidak diisi\n" % (row)
                
            # No. Tiket
            col+=1
            no_tiket = sheet.cell(row, col).value

            # No. Plat
            col+=1
            no_plat = sheet.cell(row, col).value

            # Supir
            col+=1
            driver = sheet.cell(row, col).value

            # No. Relasi
            col+=1
            relasi = sheet.cell(row, col).value

            # No. Kontrak
            col+=1
            kontrak = sheet.cell(row, col).value

            # No. DO
            col+=1
            delivery_order = sheet.cell(row, col).value

            # Asal Barang
            col+=1
            if sheet.cell(row, col).value:
                src_location = sheet.cell(row, col).value
            else:
                warning+="Data Source Location pada baris ke %s tidak diisi\n" % (row)

            # Bruto Asal
            col+=1
            if sheet.cell(row, col).value:
                if sheet.cell_type(row, col) != 2:
                    warning+="Data Bruto Asal pada baris ke %s bukan format angka\n" % (row)
                else:
                    src_bruto = sheet.cell(row, col).value
            else:
                warning+="Data Bruto Asal pada baris ke %s tidak diisi\n" % (row)

            # Tarre Asal
            col+=1
            if sheet.cell(row, col).value:
                if sheet.cell_type(row, col) != 2:
                    warning+="Data Tarre Asal pada baris ke %s bukan format angka\n" % (row)
                else:
                    src_tare = sheet.cell(row, col).value
            else:
                warning+="Data Tarre Asal pada baris ke %s tidak diisi\n" % (row)

            # Netto Asal
            col+=1
            if sheet.cell(row, col).value:
                if sheet.cell_type(row, col) != 2:
                    warning+="Data Netto Asal pada baris ke %s bukan format angka\n" % (row)
                else:
                    src_netto = sheet.cell(row, col).value
            else:
                warning+="Data Netto Asal pada baris ke %s tidak diisi\n" % (row)

            # Tujuan Akhir
            col+=1
            if sheet.cell(row, col).value:
                dest_location = sheet.cell(row, col).value
            else:
                warning+="Data Destination Location pada baris ke %s tidak diisi\n" % (row)

            # Bruto Akhir
            col+=1
            if sheet.cell(row, col).value:
                if sheet.cell_type(row, col) != 2:
                    warning+="Data Bruto Akhir pada baris ke %s bukan format angka\n" % (row)
                else:
                    dest_bruto = sheet.cell(row, col).value
            else:
                warning+="Data Bruto Akhir pada baris ke %s tidak diisi\n" % (row)

            # Tarre Akhir
            col+=1
            if sheet.cell(row, col).value:
                if sheet.cell_type(row, col) != 2:
                    warning+="Data Tarre Akhir pada baris ke %s bukan format angka\n" % (row)
                else:
                    dest_tare = sheet.cell(row, col).value
            else:
                warning+="Data Tarre Akhir pada baris ke %s tidak diisi\n" % (row)
            
            # Netto Akhir
            col+=1
            if sheet.cell(row, col).value:
                if sheet.cell_type(row, col) != 2:
                    warning+="Data Netto Akhir pada baris ke %s bukan format angka\n" % (row)
                else:
                    product_qty = sheet.cell(row, col).value
            else:
                warning+="Data Netto Akhir pada baris ke %s tidak diisi\n" % (row)

            # Produk
            col+=1
            if sheet.cell(row, col).value:
                product = sheet.cell(row, col).value
            else:
                warning+="Data Product pada baris ke %s tidak diisi\n" % (row)

            # Transportir
            col+=1
            if sheet.cell(row, col).value:
                transporter = sheet.cell(row, col).value
            else:
                warning+="Data Transporter pada baris ke %s tidak diisi\n" % (row)

            # Keterangan
            col+=1
            keterangan = sheet.cell(row, col).value

            # Rate Type
            col+=1
            try:
                rate_type = sheet.cell(row, col).value
            except:
                rate_type = 'By Weight'
           
            if not warning:
                data_matrix.append([0,False,{
                    'date' : date,
                    'no_tiket': no_tiket,
                    'no_plat': no_plat,
                    'driver_name': driver,
                    'relasi': relasi,
                    'no_kontrak': kontrak,
                    'no_do': delivery_order,
                    'src_location' : src_location,
                    'src_bruto' : src_bruto,
                    'src_tare': src_tare,
                    'src_netto': src_netto,
                    'dest_location' : dest_location,
                    'dest_bruto': dest_bruto,
                    'dest_tare': dest_tare,
                    'product_qty' : product_qty,
                    'product' : product,
                    'transporter' : transporter,
                    'keterangan': keterangan,
                    'rate_type': rate_type,
                    }])

            row+=1
        if not warning:
            self.write({'import_line': data_matrix, 'state': 'imported', 'keterangan': False})
        else:
            self.write({'keterangan': warning})

        # end of section detail
    
    
class StockTransportIMportLine(models.Model):
    _name = "stock.transport.import.line"
    _description = "Transport Import Line"

    import_id = fields.Many2one('stock.transport.import')
    date = fields.Date('Date')
    
    no_tiket = fields.Char('No. Tiket')
    no_plat = fields.Char('No. Plat')
    driver_name = fields.Char('Nama Supir')
    relasi = fields.Char('Relasi')
    no_kontrak = fields.Char('No. Kontrak')
    no_do = fields.Char('No. DO')

    src_location = fields.Char(string='Asal Barang')
    src_bruto = fields.Float(string='Bruto Asal')
    src_tare = fields.Float(string='Tarre Asal')
    src_netto = fields.Float(string='Netto Asal')

    dest_location = fields.Char(string='Tujuan Akhir')
    dest_bruto = fields.Float(string='Bruto Akhir')
    dest_tare = fields.Float(string='Tarre Akhir')
    product_qty = fields.Float(string='Netto Akhir')
    
    product = fields.Char("Product")
    transporter = fields.Char("Transportir")
    keterangan = fields.Char("Keterangan")
    rate_type = fields.Char(string='Rate Type', default='By Weight')
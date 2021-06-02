# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Hendra Saputra <hendrasaputra0501@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

import time
import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import base64
import xlrd
from xlrd import open_workbook, XLRDError
from odoo import models, fields, tools, exceptions, api, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DT
import os
import tempfile

import logging
_logger = logging.getLogger(__name__)

# INPUT DATA DATA TIMBANG: UNTUK TRANSPORTASI
class import_rekap_timbang(models.Model):
    _name = 'import.rekap.timbang'
    _inherit = ['mail.thread']
    _description = 'Import Rekap Timbang'

    name = fields.Char("Name", default="/", readonly=True, states={'draft': [('readonly',False)], 'confirm': [('readonly',False)]})
    description = fields.Char("Description", default="/", readonly=True, states={'draft': [('readonly',False)], 'confirm': [('readonly',False)]})
    book = fields.Binary(string='File Excel', readonly=True, states={'draft': [('readonly',False)], 'confirm': [('readonly',False)]})
    book_filename = fields.Char(string='File Name', readonly=True, states={'draft': [('readonly',False)], 'confirm': [('readonly',False)]})
    create_date = fields.Date('Tanggal Buat', default=fields.Date.context_today, readonly=True, states={'draft': [('readonly',False)], 'confirm': [('readonly',False)]})
    date_from = fields.Date('Date From', default=fields.Date.context_today)
    date_to = fields.Date('Date To', default=fields.Date.context_today)
    line_ids = fields.One2many('import.rekap.timbang.line', 'import_id', string="Details", readonly=True, states={'draft': [('readonly',False)], 'confirm': [('readonly',False)]})
    error_note = fields.Text("Error Note")
    note = fields.Text("Note", readonly=True, states={'draft': [('readonly',False)], 'confirm': [('readonly',False)]})
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get(), readonly=True, states={'draft': [('readonly',False)], 'confirm': [('readonly',False)]})
    state = fields.Selection(selection=[('draft', 'New'), ('imported', 'Imported'), ('confirm', 'Confirmed'), ('done', 'Invoiced'),('close','Closed')], string='Status',  copy=False, default='draft', index=False, readonly=False, track_visibility='always',)

    _order = 'create_date desc'

    @api.model
    def create(self, values):
        if values.get('name','/')=='/':
            name = self.env['ir.sequence'].next_by_code(self._name)
            values.update({'name': name})
        return super(import_rekap_timbang, self).create(values)

    @api.multi
    def unlink(self):
        for data in self:
            if data.state not in ('draft'):
                raise exceptions.UserError(_('You can not delete a manual import document when state not in draft!'))
        return super(import_rekap_timbang, self).unlink()

    @api.multi
    def set_to_draft(self):
        for data in self:
            data.state = 'draft'
            data.book = False
            data.book_filename = False
            for x in data.line_ids:
                x.unlink()

    def do_import(self):
        """
        XL_CELL_EMPTY	0	empty string ‘’
        XL_CELL_TEXT	1	a Unicode string
        XL_CELL_NUMBER	2	float
        XL_CELL_DATE	3	float
        XL_CELL_BOOLEAN	4	int; 1 means True, 0 means False
        XL_CELL_ERROR	5	int representing internal Excel codes; for a text representation, refer to the supplied dictionary error_text_from_code
        XL_CELL_BLANK	6	empty string ‘’. Note: this type will appear only when open_workbook(..., formatting_info= True) is used.
        """
        # self.error_note = ""
        rekap_line_obj = self.env['import.rekap.timbang.line']
        if not self.book:
            raise exceptions.ValidationError(_("Upload your data first!"))
        if self.line_ids:
            for lines in self.line_ids:
                lines.unlink()
        data = base64.decodestring(self.book)
        try:
            xlrd.open_workbook(file_contents=data)
        except XLRDError:
            raise exceptions.ValidationError(_("Unsupported Format!"))
        wb = xlrd.open_workbook(file_contents=data)
        total_sheet = len(wb.sheet_names())
        error_notes = []
        found_error = False
        for i in range(total_sheet):
            sheet = wb.sheet_by_index(i)
            for rows in range(sheet.nrows):
                if rows > 0:
                    mandatory_number = [3, 4, 5, 7, 8, 9]
                    mandatory_text = [0, 2, 6, 11, 12]
                    for col in range(0, 15):
                        if col in mandatory_number:
                            try:
                                x = float(str(sheet.cell_value(rows, col)).strip())
                            except:
                                found_error = True
                                error_notes.append(
                                    "Import Error Baris %s : Bruto, Tarra dan Netto harus berisi Angka" % str(rows))
                        elif col in mandatory_text:
                            if str(sheet.cell_value(rows, col)).strip() == '':
                                found_error = True
                                error_notes.append(
                                    "Import Error Baris %s : Ada kolom yang kosong. \nKolom Wajib diisi antara lain: \n \
                                    Tanggal \n Asal \n Tujuan \n Transportir \n Kontrak" % str(rows))

                    try:
                        date_str = float(str(sheet.cell_value(rows, 0)).strip())
                        seconds = (date_str - 25569) * 86400.0
                        date = datetime.datetime.utcfromtimestamp(seconds).strftime(DT)
                    except:
                        date = str(sheet.cell_value(rows, 0)).strip()
                    #Rows 1 hanya untuk title
                    rekap_line_obj.create({
                        'import_id' : self.id,
                        'date' : date,
                        'vehicle_number' : str(sheet.cell_value(rows, 1)),
                        'src_location' : str(sheet.cell_value(rows, 2)),
                        'src_bruto': str(sheet.cell_value(rows, 3)),
                        'src_tarre': str(sheet.cell_value(rows, 4)),
                        'src_netto': str(sheet.cell_value(rows, 5)),
                        'dest_location': str(sheet.cell_value(rows, 6)),
                        'dest_bruto': str(sheet.cell_value(rows, 7)),
                        'dest_tarre': str(sheet.cell_value(rows, 8)),
                        'dest_netto': str(sheet.cell_value(rows, 9)),
                        'product_name' : str(sheet.cell_value(rows, 10)),
                        'transporter' : str(sheet.cell_value(rows, 11)),
                        'contract_number': str(sheet.cell_value(rows, 12)),
                        'note': str(sheet.cell_value(rows, 13)),
                        'wb_do': str(sheet.cell_value(rows, 14)),
                        'name' : str(sheet.cell_value(rows, 15)) or '-',
                        'partner_name' : str(sheet.cell_value(rows, 16)) or '-',
                    })
        if found_error and error_notes:
            self.error_note = "\n".join(error_notes)
        else:
            self.state = 'imported'
            self.error_note = ''

    @api.multi
    def confirm(self):
        self.ensure_one()
        found_error = False
        error_notes = []
        line_grouped = {}
        for line in self.line_ids:
            # allocate transporter
            transporter = self.env['weighbridge.partner'].search([('name', '=', line.transporter)], limit=1)
            if not transporter:
                found_error = True
                error_notes.append(
                    "Tidak dapat menemukan Transportir. \nSilahkan buat Transportir atas nama %s di Master Relasi" %line.transporter)
                continue
            # allocate contract
            wb_contract = self.env['weighbridge.contract'].search([('name', '=', line.contract_number)], limit=1)
            if not wb_contract:
                found_error = True
                error_notes.append(
                    "Tidak dapat menemukan Kontrak. \nSilahkan buat Kontrak atas %s di Master Kontrak" %line.contract_number)
                continue
            else:
                line.wb_contract_id = wb_contract.id

            # allocate partner
            wb_relasi = self.env['weighbridge.partner'].search([('name', '=', line.partner_name)], limit=1)
            if not wb_relasi:
                found_error = True
                error_notes.append(
                    "Tidak dapat menemukan Relasi. \nSilahkan buat Relasi atas %s di Master Relasi" %line.partner_name)
                continue
            else:
                line.wb_partner_id = wb_relasi.id

            try:
                valid_date = datetime.datetime.strptime(line.date,'%d/%m/%Y').strftime('%Y-%m-%d')
            except:
                error_notes.append(
                    "Tidak dapat mengkonversi Format Tanggal. \nSilahkan input data Tanggal dengan format dd/mm/YYYY" %line.date)
        if found_error and error_notes:
            self.error_note = '\n'.join(list(set(error_notes)))
        else:
            self.error_note = ''
            self.state = 'confirm'

    @api.multi
    def close(self):
        self.state='closed'

class import_rekap_timbang_line(models.Model):
    _name = 'import.rekap.timbang.line'
    _description = 'Rekap Timbang Line'

    import_id = fields.Many2one('import.rekap.timbang', string="Ref", ondelete="cascade")
    date = fields.Char("Tanggal")
    name = fields.Char("Nomer Tiket")
    vehicle_number = fields.Char("No. Polisi")
    transporter = fields.Char("Transporter")
    product_name = fields.Char("Produk")
    partner_name = fields.Char("Relasi")
    contract_number = fields.Char("Kontrak")
    src_location = fields.Char("Asal")
    src_bruto = fields.Char("Bruto Asal")
    src_tarre = fields.Char("Tarra Asal")
    src_netto = fields.Char("Netto Asal")
    dest_location = fields.Char("Tujuan")
    dest_bruto = fields.Char("Bruto Akhir")
    dest_tarre = fields.Char("Tarra Akhir")
    dest_netto = fields.Char("Netto Akhir")
    remark = fields.Char("Keterangan")
    wb_do = fields.Char('Delivery Order')
    valid_date = fields.Date()
    wb_partner_id = fields.Many2one('weighbridge.partner','Relasi')
    wb_contract_id = fields.Many2one('weighbridge.contract','Kontrak')
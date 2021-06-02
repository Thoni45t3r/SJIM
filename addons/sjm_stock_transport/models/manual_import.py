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

# UNTUK IMPORT DATA TIMBANG: 99, BURSUMI, WTA PANJANG
class manual_import_dharmala(models.Model):
	_inherit = 'manual.import.dharmala'
	_description = 'Manual Import Dharmala'

	def import_manual(self):
		attendance_recap_line_obj   = self.env['manual.import.dharmala.line']
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
		error_notes  = []
		found_error = False
		for i in range(total_sheet):
			sheet = wb.sheet_by_index(i)
			for rows in range(sheet.nrows):
				#Rows 1 hanya untuk title
				if rows > 0:
					mandatory_number = [5,6,7]
					mandatory_text = [0,1,2,3,4,8,9,10]
					for col in range(0,11):
						if col in mandatory_number:
							try:
								x = float(str(sheet.cell_value(rows, col)).strip())
							except:
								found_error = True
								error_notes.append(
									"Import Error Baris %s : Bruto, Tarra dan Netto harus berisi Angka" % str(rows))
						elif col in mandatory_text:
							if str(sheet.cell_value(rows, col)).strip()=='':
								found_error = True
								error_notes.append("Import Error Baris %s : Ada kolom kosong. Setiap Kolom Wajib diisi"%str(rows))

					# tanggal
					try:
						date_str = float(str(sheet.cell_value(rows, 8)).strip())
						seconds = (date_str - 25569) * 86400.0
						date = datetime.utcfromtimestamp(seconds).strftime("%d/%m/%Y")
					except:
						date = str(sheet.cell_value(rows, 8)).strip()

					try:
						no_timbang = str(int(sheet.cell_value(rows, 1))).strip()
					except:
						no_timbang = str(sheet.cell_value(rows, 1)).strip()
					attendance_recap_line_obj.create({
						'import_id'         : self.id,
						'name'              : "Timbang " + str(sheet.cell_value(rows, 1)).strip(),
						'type'              : str(sheet.cell_value(rows, 0)).strip(),
						'no_timbang'        : no_timbang,
						'no_pol'            : str(sheet.cell_value(rows, 2)).strip(),
						'vendor'            : str(sheet.cell_value(rows, 3)).strip(),
						'kontrak'           : str(sheet.cell_value(rows, 4)).strip(),
						'bruto'             : str(sheet.cell_value(rows, 5)).strip(),
						'tarra'             : str(sheet.cell_value(rows, 6)).strip(),
						'netto'             : str(sheet.cell_value(rows, 7)).strip(),
						'date'              : date,
						'transporter'       : str(sheet.cell_value(rows, 9)).strip(),
						'product'           : str(sheet.cell_value(rows, 10)).strip(),
						'note'              : str(sheet.cell_value(rows, 11)).strip(),
						'driver_name'		: str(sheet.cell_value(rows, 12)).strip(),
						'wb_do'             : str(sheet.cell_value(rows, 13)).strip(),
					})
		if found_error and error_notes:
			self.error_note = "\n".join(list(set(error_notes)))
		else:
			self.state = 'imported'
			self.error_note = ''

class manual_import_dharmala_line(models.Model):
	_inherit = 'manual.import.dharmala.line'
	_description = 'Manual Import Dharmala Line'

	transport_move_id = fields.Many2one("stock.transport.move", "Transport Move ID")
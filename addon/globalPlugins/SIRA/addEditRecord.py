# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

Created on: 08/01/2025.
"""

import os
import re
import sys

import addonHandler
import config
import gui
import wx
from logHandler import log

from . import controller as core
from .varsConfig import ADDON_PATH, is64, ADDON_NAME

# Add the lib/ folder to sys.path (only once)
libFolder = "lib64" if is64 else "lib"
libPath = os.path.join(ADDON_PATH, libFolder)

if os.path.isdir(libPath) and libPath not in sys.path:
	sys.path.insert(0, libPath)

try:
	from masked.textctrl import TextCtrl
except ImportError as e:
	log.error(f"[{ADDON_NAME}] Error when importing internal library 'masked': {e}")
	raise ImportError(_("Mandatory Library Absent: Masked"))

# Global Constants for Regex
EMAIL_REGEX = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}$"

def validate_fields(data):
	"""
	Validates the fields of the contact form.

	Args:
		data (dict): Data from the form to be validated.

	Returns:
		dict: A dictionary of errors with the invalid fields and their respective messages.
	"""
	errors = {}

	# Validation of mandatory fields is essential to avoid corrupted data.
	if not data.get("secretary_office"):
		errors["secretary_office"] = _("It is necessary to inform the secretary office!")
	if not data.get("landline"):
		errors["landline"] = _("It is necessary to inform the landline!")
	if not data.get("extension"):
		errors["extension"] = _("It is necessary to inform the extension!")
	
	# Email validation is done only if the field is not empty.
	if data.get("email") and not re.match(EMAIL_REGEX, data["email"]):
		errors["email"] = _("Invalid email format!")

	return errors

# Initialize translation support
addonHandler.initTranslation()


class AddEditRecDialog(wx.Dialog):

	def __init__(self, parent, row=None, title=_("Add"), addRecord=True):
		self.title = title
		WIDTH = 600
		HEIGHT = 400

		wx.Dialog.__init__(self, parent, title=_("{} extensions.").format(title), size=(WIDTH, HEIGHT))

		# Get the configuration for this add-on.
		conf = config.conf.get(ADDON_NAME)

		if conf is None:
			conf = config.conf[ADDON_NAME]

		self.formatLandline = conf.get("formatLandline") or "(##) ####-####" 
		self.formatCellPhone = conf.get("formatCellPhone") or "(##) #####-####"
		self.addRecord = addRecord
		self.selectedRow = row

		# Simplification of startup of variables using a conditional expression
		secretary_office = row.secretary_office if row else ""
		landline = row.landline if row else ""
		sector = row.sector if row else ""
		responsible = row.responsible if row else ""
		extension = row.extension if row else ""
		cell = row.cell if row else ""
		email = row.email if row else ""
		
		# Widget Creation
		self.panel = wx.Panel(self)

		labelSecretary = wx.StaticText(self.panel, label=_("Secretary: "))
		self.textSecretary_office = wx.TextCtrl(self.panel, value=secretary_office, style=wx.TE_PROCESS_ENTER)

		labelLandline = wx.StaticText(self.panel, label=_("Landline: "))
		self.textLandline = TextCtrl(self.panel, value=landline, mask=self.formatLandline, style=wx.TE_PROCESS_ENTER)

		labelSector = wx.StaticText(self.panel, label=_("Sector: "))
		self.textSector = wx.TextCtrl(self.panel, value=sector, style=wx.TE_PROCESS_ENTER)

		labelResponsible = wx.StaticText(self.panel, label=_("Responsible: "))
		self.textResponsible = wx.TextCtrl(self.panel, value=responsible, style=wx.TE_PROCESS_ENTER)

		labelExtension = wx.StaticText(self.panel, label=_("Extension: "))
		self.textExtension = TextCtrl(self.panel, value=extension, mask=("####"), style=wx.TE_PROCESS_ENTER)

		labelCell = wx.StaticText(self.panel, label=_("Cell phone: "))
		self.textCell = TextCtrl(self.panel, value=cell, mask=self.formatCellPhone, style=wx.TE_PROCESS_ENTER)

		labelEmail = wx.StaticText(self.panel, label=_("Email: "))
		self.textEmail = wx.TextCtrl(self.panel, value=email, style=wx.TE_PROCESS_ENTER)

		self.buttonOk = wx.Button(self.panel, wx.ID_OK, label=_("&Ok"))
		self.buttonOk.Bind(wx.EVT_BUTTON, self.handleRecord)

		self.buttonCancel = wx.Button(self.panel, wx.ID_CANCEL, label=_("&Cancel"))
		self.buttonCancel.Bind(wx.EVT_BUTTON, self.onCancel)

		# Layout structure
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		viewSizer = wx.BoxSizer(wx.VERTICAL)
		viewSizer.Add(labelSecretary, 0, wx.ALL | wx.EXPAND, 5)
		viewSizer.Add(self.textSecretary_office, 0, wx.ALL | wx.EXPAND, 5)
		viewSizer.Add(labelLandline, 0, wx.ALL | wx.EXPAND, 5)
		viewSizer.Add(self.textLandline, 0, wx.ALL | wx.EXPAND, 5)
		viewSizer.Add(labelSector, 0, wx.ALL | wx.EXPAND, 5)
		viewSizer.Add(self.textSector, 0, wx.ALL | wx.EXPAND, 5)
		viewSizer.Add(labelResponsible, 0, wx.ALL | wx.EXPAND, 5)
		viewSizer.Add(self.textResponsible, 0, wx.ALL | wx.EXPAND, 5)
		viewSizer.Add(labelExtension, 0, wx.ALL | wx.EXPAND, 5)
		viewSizer.Add(self.textExtension, 0, wx.ALL | wx.EXPAND, 5)
		viewSizer.Add(labelCell, 0, wx.ALL | wx.EXPAND, 5)
		viewSizer.Add(self.textCell, 0, wx.ALL | wx.EXPAND, 5)
		viewSizer.Add(labelEmail, 0, wx.ALL | wx.EXPAND, 5)
		viewSizer.Add(self.textEmail, 0, wx.ALL | wx.EXPAND, 5)

		buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
		buttonSizer.Add(self.buttonOk, 0, wx.ALL, 5)
		buttonSizer.Add(self.buttonCancel, 0, wx.ALL, 5)

		mainSizer.Add(viewSizer, wx.EXPAND)
		mainSizer.Add(buttonSizer, 0, wx.CENTER)
		self.panel.SetSizerAndFit(mainSizer)

		# Bindings to move the focus by pressing Enter into the fields of text
		self.textSecretary_office.Bind(wx.EVT_TEXT_ENTER, self.onFocusSecretary)
		self.textSector.Bind(wx.EVT_TEXT_ENTER, self.onFocusSector)
		self.textResponsible.Bind(wx.EVT_TEXT_ENTER, self.onFocusResponsible)
		self.textEmail.Bind(wx.EVT_TEXT_ENTER, self.onFocusEmail)

	def onFocusSecretary(self, event):
		self.textLandline.SetFocus()

	def onFocusLandline(self, event):
		self.textSector.SetFocus()

	def onFocusSector(self, event):
		self.textResponsible.SetFocus()

	def onFocusResponsible(self, event):
		self.textExtension.SetFocus()

	def onFocusExtension(self, event):
		self.textCell.SetFocus()

	def onFocusCell(self, event):
			self.textEmail.SetFocus()

	def onFocusEmail(self, event):
		self.buttonOk.SetFocus()
	
	def getData(self):
		"""
		Collect and validate the contact form data.

		Returns:
			dict or None: A dictionary with contact data if valid or none if there are errors.
		"""
		# Form data collection
		contactDict = {
			"secretary_office": self.textSecretary_office.GetValue().strip(),
			"landline": self.textLandline.GetValue().strip(),
			"sector": self.textSector.GetValue().strip(),
			"responsible": self.textResponsible.GetValue().strip(),
			"extension": self.textExtension.GetValue().strip(),
			"cell": self.textCell.GetValue().strip(),
			"email": self.textEmail.GetValue().strip()
		}

		errors = validate_fields(contactDict)
		if errors:
			# Take the first error and display the message
			field, message = next(iter(errors.items()))
			self.show_message(message, _("Error"))
			self.focus_field(field)
			return None

		return contactDict

	def onAdd(self):
		"""
		Adds new contact to the database and displays confirmation or error messages.
		"""
		contactDict = self.getData()
		if not contactDict:
			return

		data = {"contacts": contactDict}
		success, error = self.save_contact_to_db(data)

		if success:
			message = _("Contact added, want to add a new contact?")
			caption = _("Success")
			user_response = gui.messageBox(message, caption, style=wx.ICON_QUESTION | wx.YES_NO)
			if user_response == wx.YES:
				self.clear_form()
			else:
				self.Destroy()
		else:
			self.show_message(_("Error adding contact: {}").format(error), _("Error"), wx.ICON_ERROR)

	def save_contact_to_db(self, data):
		"""
		Save a contact in the database.

		Args:
			data (dict): Contact data to be saved.

		Returns:
			tuple: A boolean indicating success or failure, and an error message in case of failure.
		"""
		try:
			core.add_record(data)
			return True, None
		except Exception as e:
			return False, str(e)

	def focus_field(self, field_name):
		"""
		Defines the focus on the field corresponding to the name of the provided field.

		Args:
			field_name (str): Name of the field to be focused.
		"""
		focus_mapping = {
			"secretary_office": self.textSecretary_office,
			"landline": self.textLandline,
			"sector": self.textSector,
			"responsible": self.textResponsible,
			"extension": self.textExtension,
			"cell": self.textCell,
			"email": self.textEmail,
		}
		if field_name in focus_mapping:
			focus_mapping[field_name].SetFocus()

	def onEdit(self):
		"""
		Edits the selected contact in the database and displays a success message to the user.
		"""
		contactDict = self.getData()
		if not contactDict:
			return

		try:
			core.edit_record(self.selectedRow.id, contactDict)
			self.show_message(_("Contact edited!"), _("Success"), wx.ICON_INFORMATION)
			self.Destroy()
		except Exception as e:
			self.show_message(_("Error editing contact: {}").format(str(e)), _("Error"), wx.ICON_ERROR)

	def handleRecord(self, event):
		"""
		Adds or edits a contact based on the form's current state.
		"""
		if self.addRecord:
			self.onAdd()
		else:
			self.onEdit()

	def show_message(self, message, caption=_("Message"), style=wx.OK | wx.ICON_INFORMATION):
		"""
		Displays a message to the user in a dialog box.
		"""
		gui.messageBox(message, caption, style)

	def clear_form(self):
		"""
		Cleans the fields of the form and position the focus on the first field.
		"""
		# Cleaning of safer and direct fields
		self.textSecretary_office.SetValue("")
		self.textLandline.SetValue("")
		self.textSector.SetValue("")
		self.textResponsible.SetValue("")
		self.textExtension.SetValue("")
		self.textCell.SetValue("")
		self.textEmail.SetValue("")
		self.textSecretary_office.SetFocus()

	def onCancel(self, event):
		"""
		Handles the cancel event by destroying the current window.
		"""
		self.Destroy()

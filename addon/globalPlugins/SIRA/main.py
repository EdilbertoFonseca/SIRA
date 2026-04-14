# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 - 2026 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

-------------------------------------------------------------------------
AI DISCLOSURE / NOTA DE IA:
This project utilizes AI for code refactoring and logic suggestions.
All AI-generated code was manually reviewed and tested by the author.
-------------------------------------------------------------------------

Created on: 30/11/2022.
"""

import os

import addonHandler
import config
import gui
import ui
import wx
from gui import guiHelper

from . import controller as core
from .addEditRecord import AddEditRecDialog
from .varsConfig import ADDON_NAME
from .manageDuplicatesDialog import ManageDuplicatesDialog

# Initializes the translation
addonHandler.initTranslation()


class SIRA(wx.Dialog):
	_instance = None

	def __new__(cls, *args, **kwargs):
		# Make this a singleton.
		if SIRA._instance is None:
			return super(SIRA, cls).__new__(cls, *args, **kwargs)
		return SIRA._instance

	def __init__(self, parent, title):
		if SIRA._instance is not None:
			return
		SIRA._instance = self

		# Title of Extension Registration System dialog.
		self.title = title

		WIDTH = 800
		HEIGHT = 400

		try:
			self.contactResults = core.getAllRecords()
		except EOFError:
			self.contactResults = []

		super(SIRA, self).__init__(
			parent,
			title=title,
			size=(WIDTH, HEIGHT),
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
		)
		self.Bind(wx.EVT_WINDOW_DESTROY, self._onInternalDestroy)
		self.Bind(wx.EVT_CHAR_HOOK, self.onKeyPress)

		# Creating the screen objects.
		panel = wx.Panel(self)
		self.contactList = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
		self._create_columns()
		self.contactList.Bind(wx.EVT_CHAR_HOOK, self.whenPressingLetters)
		self._itemMap = {}
		self.initialize_contact_list()
		self.contactList.SetFocus()

		# Selected line viewing field
		self.visualizationField = wx.TextCtrl(
			panel,
			style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_STATIC,
		)

		# Translators: Search field label.
		labelSearch = wx.StaticText(panel, label=_("Search for: "))

		# List of combobox choices option.
		listOfOptions = [
			_("Secretary office"),
			_("Landline"),
			_("Sector"),
			_("Responsible"),
			_("Extension"),
			_("Cell phone"),
			_("Email"),
		]
		self.comboboxOptions = wx.ComboBox(panel, value=_("Secretary office"), choices=listOfOptions)

		self.search = wx.SearchCtrl(panel, -1, size=(250, 25))
		self.buttonSearch = wx.Button(panel, label=_("&Search"))

		# Selection event
		self.contactList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelectLine)

		self.buttonEdit = wx.Button(panel, wx.ID_EDIT, label=_("&Edit"))
		self.buttonNew = wx.Button(panel, wx.ID_NEW, label=_("&New"))
		self.buttonDelete = wx.Button(panel, wx.ID_DELETE, label=_("&Remove"))
		self.buttonFindDuplicates = wx.Button(panel, label=_("Find Duplicates"))
		self.buttonSaveResearch = wx.Button(panel, wx.ID_SAVE, label=_("&Save the research"))
		self.buttonRefresh = wx.Button(panel, -1, label=_("Refres&h"))
		self.buttonImport = wx.Button(panel, -1, label=_("&Import csv..."))
		self.buttonExport = wx.Button(panel, -1, label=_("E&xport csv..."))
		self.buttonResetRecords = wx.Button(panel, -1, label=_("&Delete all records."))
		self.buttonExit = wx.Button(panel, wx.ID_CANCEL, label=_("Exi&t"))
		self.set_config()

		# Creating the layout and adding it to the panel.
		boxSizer = wx.BoxSizer(wx.VERTICAL)
		viewSizer = wx.BoxSizer(wx.VERTICAL)
		searchSizer = wx.BoxSizer(wx.HORIZONTAL)
		buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

		viewSizer.Add(self.contactList, 1, wx.ALL | wx.EXPAND, 10)
		searchSizer.Add(labelSearch, 0, wx.ALL, 5)
		searchSizer.Add(self.comboboxOptions, 0, wx.ALL, 5)
		searchSizer.Add(self.search, 1, wx.ALL, 5)
		searchSizer.Add(self.buttonSearch, 0, wx.ALL, 5)

		buttonSizer.Add(self.buttonEdit, 0, wx.ALL | wx.EXPAND, 5)
		buttonSizer.Add(self.buttonDelete, 0, wx.ALL | wx.EXPAND, 5)
		buttonSizer.Add(self.buttonFindDuplicates, 0, wx.ALL, 5)
		buttonSizer.Add(self.buttonSaveResearch, 0, wx.ALL | wx.EXPAND, 5)
		buttonSizer.Add(self.buttonRefresh, 0, wx.ALL | wx.EXPAND, 5)
		buttonSizer.Add(self.buttonImport, 0, wx.ALL | wx.EXPAND, 5)
		buttonSizer.Add(self.buttonExport, 0, wx.ALL | wx.EXPAND, 5)
		buttonSizer.Add(self.buttonResetRecords, 0, wx.ALL | wx.EXPAND, 5)
		buttonSizer.Add(self.buttonExit, 0, wx.ALL | wx.EXPAND, 5)

		# Define the main layout of the window
		boxSizer.Add(searchSizer, wx.ALL, guiHelper.BORDER_FOR_DIALOGS)
		boxSizer.Add(viewSizer, wx.ALL, guiHelper.BORDER_FOR_DIALOGS)
		boxSizer.Add(buttonSizer, 0, wx.CENTER)
		panel.SetSizerAndFit(boxSizer)
		self.Fit()

		# Binding events to buttons.
		self.buttonSearch.Bind(wx.EVT_BUTTON, self.onSearch, self.buttonSearch)
		self.buttonEdit.Bind(wx.EVT_BUTTON, self.onEdit, self.buttonEdit)
		self.buttonNew.Bind(wx.EVT_BUTTON, self.onNew, self.buttonNew)
		self.buttonDelete.Bind(wx.EVT_BUTTON, self.onDelete, self.buttonDelete)
		self.buttonFindDuplicates.Bind(wx.EVT_BUTTON, self.onFindDuplicates, self.buttonFindDuplicates)
		self.buttonSaveResearch.Bind(wx.EVT_BUTTON, self.onSaveResearchResults, self.buttonSaveResearch)
		self.buttonRefresh.Bind(wx.EVT_BUTTON, self.onToUpdate, self.buttonRefresh)
		self.buttonImport.Bind(wx.EVT_BUTTON, self.onToImport, self.buttonImport)
		self.buttonExport.Bind(wx.EVT_BUTTON, self.onToExport, self.buttonExport)
		self.buttonResetRecords.Bind(wx.EVT_BUTTON, self.onReset, self.buttonResetRecords)
		self.buttonExit.Bind(wx.EVT_BUTTON, self.onClose, self.buttonExit)

	def _create_columns(self):
		columns = [
			(_("Secretary office"), 150),
			(_("Landline"), 100),
			(_("Sector"), 150),
			(_("Responsible"), 150),
			(_("Extension"), 100),
			(_("Cell phone"), 100),
			(_("Email"), 300),
		]

		for i, (label, width) in enumerate(columns):
			self.contactList.InsertColumn(i, label)
			self.contactList.SetColumnWidth(i, width)

	def initialize_contact_list(self):
		self.contactList.DeleteAllItems()

		self._itemMap = {}

		for record in self.contactResults:
			index = self.contactList.InsertItem(
				self.contactList.GetItemCount(),
				record.secretaryOffice,
			)

			record_values = (
				record.landline,
				record.sector,
				record.responsible,
				record.extension,
				record.cell,
				record.email,
			)

			for colIndex, value in enumerate(record_values, start=1):
				self.contactList.SetItem(index, colIndex, value)

			self._itemMap[index] = record

	def onNew(self, event):
		"""Add a new record to the agenda."""
		dlg = AddEditRecDialog(gui.mainFrame)
		gui.mainFrame.prePopup
		dlg.CentreOnScreen()
		dlg.ShowModal()
		dlg.Destroy()
		gui.mainFrame.postPopup
		self._refresh_and_focus()

	def onEdit(self, event):
		"""Edit a selected record."""
		selectedRow = self.get_selected_record()
		if selectedRow is None:
			self.showMessage(_("No records selected!"), _("Error"))
			return
		dlg = AddEditRecDialog(
			gui.mainFrame,
			selectedRow,
			title=_("To edit"),
			addRecord=False,
		)
		gui.mainFrame.prePopup
		dlg.CentreOnScreen()
		dlg.ShowModal()
		dlg.Destroy()
		gui.mainFrame.postPopup
		self._refresh_and_focus()

	def onDelete(self, event):
		"""
		Deletes the selected record in the contact list after user confirmation.

		Args:
			event (wx.Event): The event that triggered this function.
		"""
		selectedRow = self.get_selected_record()
		if selectedRow is None:
			self.showMessage(_("No records selected!"), _("Error"))
			return

		message = _("Do you want to delete the selected record?")
		caption = _("Attention")

		user_response = gui.messageBox(message, caption, style=wx.ICON_QUESTION | wx.YES_NO)
		if user_response == wx.YES:
			try:
				core.delete(selectedRow.id)
				self.showMessage(_("Record deleted!"), _("Success"))
				self._refresh_and_focus()
			except Exception as e:
				self.showMessage(_("Error deleting record: {}").format(str(e)), _("Error"))
				return
		self.contactList.SetFocus()

	def onSearch(self, event):
		"""Search using all the fields of the agenda."""
		# Gets the chosen filter option and the entered keyword
		filterChoice = self.comboboxOptions.GetValue()
		keyword = self.search.GetValue()

		if not keyword or keyword.strip() == "":
			self.showMessage(_("The search field is empty!"), _("Attention"))
			self.search.SetFocus()
			return

		# Try to search based on filter and keyword option
		try:
			# Call the search function in the core module, passing the filter and keyword option
			self.contactResults = core.searchRecords(filterChoice, keyword)

			# Check if there were any results returned by the search
			if not self.contactResults:
				# If there are no results, displays an informative message
				self.showMessage(_("No contacts found matching the search criteria."))
				self.search.SetFocus()
			else:
				# Otherwise, update the contact list in the graphical interface
				self.initialize_contact_list()

				# Clear the search field after searching
				self.search.Clear()

				# Sets focus back to the contact list for easier navigation
				self.contactList.SetFocus()
		except Exception as e:
			# Display an error message if an exception occurs during the search
			self.showMessage("{}".format(e))

	def onToImport(self, event):
		"""Import csv file to the List of extensions."""
		dlg = wx.FileDialog(
			self,
			_("import csv file"),
			os.getcwd(),
			"",
			"*.csv",
			wx.FD_OPEN,
		)
		if dlg.ShowModal() == wx.ID_OK:
			try:
				mypath = dlg.GetPath()
				core.importCsvToDb(mypath)
				self.showMessage(_("File imported successfully!"), _("Attention"))
				self._refresh_and_focus()
			except Exception as e:
				msg = _(
					"""It was not possible to import the file! {}""".format(str(e)),
				)

				# Translators: Message displayed to the user in case of errors when importing the CSV file
				self.showMessage(msg, _("Attention"))
		dlg.Destroy()
		self.contactList.SetFocus()

	def onToExport(self, event):
		"""Export the List of extensions to csv."""
		dlg = wx.FileDialog(
			self,
			_("export csv file"),
			os.getcwd(),
			_("List of extensions"),
			"*.csv",
			wx.FD_SAVE,
		)
		if dlg.ShowModal() == wx.ID_OK:
			try:
				mypath = dlg.GetPath()
				core.exportDBToCsv(mypath)
				self.showMessage(_("File exported successfully!"), _("Attention"))
				self.contactList.SetFocus()
			except Exception as e:
				msg = _(
					"""It was not possible to export the file! {}""".format(e),
				)

				# Translators: Message displayed to the user in case of errors when exporting the CSV file
				self.showMessage(msg, _("Attention"))
		dlg.Destroy()
		self.contactList.SetFocus()

	def onReset(self, event):
		"""
		Resets all phonebook records after user confirmation.

		Args:
			event (wx.Event): The event that triggered this function.
		"""

		# 1. Obtains the counting of records safely.
		record_count = core.countRecords()

		# 2. Checks the three possible scenarios: failure, empty list or list with records.
		if record_count is None:
			# If Record Count for None, there was an error in the database.
			# The error message is already displayed internally by the Core.COUNT Records function.
			self.showMessage(_("An error occurred while counting records. Check the logs."), _("Error"))
			return

		elif record_count == 0:
			# If Record Count for 0, the agenda is already empty.
			self.showMessage(_("The agenda is already empty!"), _("Attention"))
			return

		# 3. If Record Count> 0, requests user confirmation.
		message = _("This operation erases all phonebook entries. Do you wish to continue?")
		caption = _("Attention")

		user_response = gui.messageBox(message, caption, style=wx.ICON_QUESTION | wx.YES_NO)
		if user_response == wx.YES:
			try:
				core.resetRecord()
				self.showMessage(_("Agenda deleted!"), _("Success"))
				self._refresh_and_focus()
			except Exception as e:
				self.showMessage(_("Error deleting records: {}").format(str(e)), _("Error"))
				return

		# 4. Refreshes the list and sets focus, encapsulating repeated calls.
		self._refresh_and_focus()

	def set_config(self):
		"""
		Apply configurations specific to the add-on
		"""
		conf = config.conf.get(ADDON_NAME, {})

		if not conf.get("resetRecords", True):
			self.buttonResetRecords.Disable()

		if not conf.get("importCSV", True) or not conf.get("exportCSV", True):
			self.buttonExport.Disable()
			self.buttonImport.Disable()

	def onFindDuplicates(self, event):
		"""
		Busca e, se houver, exibe registros duplicados para o usuário em um novo diálogo.
		"""
		duplicates = core.findDuplicateRecords()

		if duplicates:
			# Abre o novo diálogo para o usuário gerenciar as duplicatas
			dlg = ManageDuplicatesDialog(self, duplicates)
			gui.mainFrame.prePopup()
			dlg.CentreOnScreen()
			dlg.ShowModal()
			dlg.Destroy()
			gui.mainFrame.postPopup()
		else:
			gui.messageBox(
				_("No duplicate records were found."),
				_("No Duplicates Found"),
				style=wx.ICON_INFORMATION,
			)

	def onSaveResearchResults(self, event):
		"""
					Saves ObjectlistView's filtered results in a CSV file.

					This function extracts the filtered items from the contact list and allows the user to choose a location to save the data in CSV format.
					If there are no results to save, a warning message is displayed.
					If an error occurs during the export process, an error message will be shown.

				Args:
					event (wx.Event): The event that called the function, usually an event of
																button click or interface action.

				Exceptions:
		If an error occurs when saving the CSV file, an error message will be shown
					with details about the problem.
		"""

		# We extracted the item using the Getobject method
		filtered_item = self.contactResults

		# Check if the item was found
		if not filtered_item:
			self.showMessage("No results found to save.", "Warning")
			return

		dlg = wx.FileDialog(
			self,
			_("export csv file"),
			os.getcwd(),
			_("List of extensions"),
			"*.csv",
			wx.FD_SAVE,
		)
		if dlg.ShowModal() == wx.ID_OK:
			try:
				mypath = dlg.GetPath()
				core.saveCsv(filtered_item, mypath)
				self.showMessage(_("File exported successfully!"), _("Attention"))
				self.contactList.SetFocus()
			except Exception as e:
				msg = _(
					"""It was not possible to export the file! {}""".format(e),
				)

				# Translators: Message displayed to the user in case of errors when exporting the CSV file
				self.showMessage(msg, _("Attention"))
		dlg.Destroy()
		self.contactList.SetFocus()

	def showMessage(self, message, caption=None, style=wx.OK | wx.ICON_INFORMATION):
		"""
		Displays a message to the user in a dialog box.

		Args:
			message (str): The message to be displayed.
			caption (str, optional): The title of the dialog box. The default is ("Message").
			style (int, optional): The style of the dialog box,
			combining flags like wx.OK,
			wx.CANCEL, wx.ICON INFORMATION, etc. The default is wx.OK | wx.ICON_INFORMATION.
		"""
		if caption is None:
			caption = _("Message")
		gui.messageBox(message, caption, style)

	def onKeyPress(self, event):
		"""
		Handles key press events in the dialog.
		"""
		keyCode = event.GetKeyCode()
		focused = self.FindFocus()

		if keyCode == wx.WXK_F5:
			self.onToUpdate(event)

		elif keyCode == wx.WXK_DELETE:
			# Checks if focus is on an edit field
			if isinstance(focused, (wx.TextCtrl, wx.SearchCtrl)):
				event.Skip()
				return
			self.onDelete(event)

		elif keyCode == wx.WXK_F2:
			self.onEdit(event)

		elif keyCode == wx.WXK_RETURN:
			# If the focus is on the search, execute the search
			if focused == self.search:
				self.onSearch(event)
			else:
				event.Skip()  # Allows default behavior in other fields
		else:
			# For any other key, let the system process normally
			event.Skip()

	def onClose(self, event):
		"""
		closes the window.

		Args:
			event (wx.Event): Event triggered by the cancel button.
		"""
		self.Destroy()

	def get_selected_record(self):
		idx = self.contactList.GetFirstSelected()
		if idx == -1:
			return None
		return self._itemMap.get(idx)

	def show_all_records(self):
		self.contactResults = core.getAllRecords()
		self.initialize_contact_list()

	def _refresh_and_focus(self):
		"""
		Refreshes the contact list and sets the focus to it.
		"""

		self.show_all_records()
		self.visualizationField.SetValue("")
		self.contactList.SetFocus()

	def onToUpdate(self, event):
		self._refresh_and_focus()
		ui.message(_("Updated records!"))

	def onSelectLine(self, event):
		# Check if there is a line selected in the list
		selected_idx = self.contactList.GetFirstSelected()
		if selected_idx == -1:
			return

		data = [
			f"{self.contactList.GetColumn(i).GetText()}: {self.contactList.GetItem(selected_idx, i).GetText()}"
			for i in range(self.contactList.GetColumnCount())
		]
		lineComplete = " | ".join(data)
		self.visualizationField.SetValue(lineComplete)

	def whenPressingLetters(self, event):
		code = event.GetKeyCode()

		if code >= 256:
			event.Skip()
			return

		try:
			key = chr(code).upper()
		except Exception:
			event.Skip()
			return

		# Mapping key column
		map = {
			"S": 0,  # Secretary
			"L": 1,  # Landline
			"C": 2,  # Sector
			"R": 3,  # Responsible
			"M": 4,  # Ramal:
			"P": 5,  # Cell phone
			"E": 6,  # Email
		}

		if key not in map:
			event.Skip()
			return

		idx = self.contactList.GetFirstSelected()
		if idx == -1:
			event.Skip()
			return

		column = map[key]

		text = self.contactList.GetItemText(idx, column)

		if text:
			ui.message(text)
		else:
			ui.message(_("Empty"))

	def _onInternalDestroy(self, evt):
		# Limpa a instância do Singleton para que o próximo __new__ crie uma nova
		SIRA._instance = None
		evt.Skip()

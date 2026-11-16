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

Created on: 25/02/2025
"""

import os
from pathlib import Path

import addonHandler
import globalVars
import wx
from gui import guiHelper
from gui.settingsDialogs import SettingsPanel

from .dbConfig import DatabaseConfig
from .varsConfig import (
	ADDON_SUMMARY,
	getFormatCellPhone,
	getFormatLandline,
	getRemoveConfigOnUninstall,
	getResetRecords,
	getImportCSV,
	getExportCSV,
	setFormatCellPhone,
	setFormatLandline,
	setRemoveConfigOnUninstall,
	setResetRecords,
	setImportCSV,
	setExportCSV,
)

# Initialize translation
addonHandler.initTranslation()


class SIRASystemSettingsPanel(SettingsPanel):
	title = ADDON_SUMMARY

	def makeSettings(self, sizer: wx.BoxSizer):
		"""
		Create and organize the SIRA settings controls.
		"""
		settingsSizer = wx.BoxSizer(wx.VERTICAL)

		settingsSizerHelper = guiHelper.BoxSizerHelper(
			self,
			sizer=settingsSizer,
		)

		# Initialize database configuration.
		self.dbConfig = DatabaseConfig(
			defaultPath=Path(globalVars.appArgs.configPath) / "SIRA_DB" / "database.db",
		)
		self.dbConfig.loadConfig()

		# GROUP 1: Phone field masks.
		phoneBoxSizer = wx.StaticBoxSizer(
			wx.VERTICAL,
			self,
			label=_("Phone field masks:"),
		)

		phoneBox = phoneBoxSizer.GetStaticBox()
		phoneGrid = wx.FlexGridSizer(cols=2, vgap=10, hgap=10)
		phoneGrid.AddGrowableCol(1, 1)

		# Cell phone mask.
		cellPhoneLabel = wx.StaticText(
			phoneBox,
			label=_("Cell phone:"),
		)

		self.textCellPhone = wx.TextCtrl(phoneBox)
		self.textCellPhone.SetValue(getFormatCellPhone())

		phoneGrid.Add(
			cellPhoneLabel,
			0,
			wx.ALIGN_CENTER_VERTICAL,
		)
		phoneGrid.Add(
			self.textCellPhone,
			1,
			wx.EXPAND,
		)

		# Landline mask.
		landlineLabel = wx.StaticText(
			phoneBox,
			label=_("Landline:"),
		)

		self.textLandline = wx.TextCtrl(phoneBox)
		self.textLandline.SetValue(getFormatLandline())

		phoneGrid.Add(
			landlineLabel,
			0,
			wx.ALIGN_CENTER_VERTICAL,
		)
		phoneGrid.Add(
			self.textLandline,
			1,
			wx.EXPAND,
		)

		phoneBoxSizer.Add(
			phoneGrid,
			1,
			wx.ALL | wx.EXPAND,
			10,
		)

		settingsSizerHelper.addItem(phoneBoxSizer)

		# GROUP 2: General options.
		optionsBoxSizer = wx.StaticBoxSizer(
			wx.VERTICAL,
			self,
			label=_("General Options:"),
		)

		optionsBox = optionsBoxSizer.GetStaticBox()

		self.removeConfigOnUninstall = wx.CheckBox(
			optionsBox,
			label=_("Remove settings on uninstall"),
		)
		self.removeConfigOnUninstall.SetValue(
			getRemoveConfigOnUninstall(),
		)

		self.resetRecords = wx.CheckBox(
			optionsBox,
			label=_("Show option to delete entire calendar"),
		)
		self.resetRecords.SetValue(getResetRecords())

		self.importCSV = wx.CheckBox(
			optionsBox,
			label=_("Show import CSV button"),
		)
		self.importCSV.SetValue(getImportCSV())

		self.exportCSV = wx.CheckBox(
			optionsBox,
			label=_("Show export CSV button"),
		)
		self.exportCSV.SetValue(getExportCSV())

		for control in (
			self.removeConfigOnUninstall,
			self.resetRecords,
			self.importCSV,
			self.exportCSV,
		):
			optionsBoxSizer.Add(
				control,
				0,
				wx.ALL,
				5,
			)

		settingsSizerHelper.addItem(optionsBoxSizer)

		# GROUP 3: Database management.
		pathBoxSizer = wx.StaticBoxSizer(
			wx.VERTICAL,
			self,
			label=_("Database Management:"),
		)

		pathBox = pathBoxSizer.GetStaticBox()

		# Database path selection.
		pathControlSizer = wx.BoxSizer(wx.HORIZONTAL)

		pathLabel = wx.StaticText(
			pathBox,
			label=_("Current database path:"),
		)

		displayPaths = self._getDatabaseChoices()

		self.pathNameCB = wx.Choice(
			pathBox,
			choices=displayPaths,
		)
		self.pathNameCB.SetSelection(self.dbConfig.indexDB)

		pathControlSizer.Add(
			pathLabel,
			0,
			wx.ALL | wx.ALIGN_CENTER_VERTICAL,
			5,
		)
		pathControlSizer.Add(
			self.pathNameCB,
			1,
			wx.ALL | wx.EXPAND,
			5,
		)

		pathBoxSizer.Add(
			pathControlSizer,
			0,
			wx.ALL | wx.EXPAND,
			5,
		)

		# Button to select or add a database directory.
		self.changePathBtn = wx.Button(
			pathBox,
			label=_("&Select or add a directory"),
		)
		self.changePathBtn.Bind(
			wx.EVT_BUTTON,
			self.onSelectDirectory,
		)

		pathBoxSizer.Add(
			self.changePathBtn,
			0,
			wx.ALL | wx.CENTER,
			5,
		)

		settingsSizerHelper.addItem(pathBoxSizer)

		# Add the complete settings layout to the NVDA panel.
		sizer.Add(
			settingsSizer,
			flag=wx.EXPAND,
			proportion=1,
		)

	def _getDatabaseChoices(self) -> list[str]:
		"""
		Return the database paths displayed in the selection control.
		"""
		return [
			self.dbConfig.firstDatabase,
			self.dbConfig.altDatabase if self.dbConfig.altDatabase else _("Empty (Not configured)"),
		]

	def onSelectDirectory(self, event):
		"""
		Select or add a database file.
		"""
		currentPath = self.dbConfig.getCurrentDatabasePath()

		initialDir = os.path.dirname(currentPath) if currentPath else os.path.expanduser("~")

		dlg = wx.FileDialog(
			self,
			_("Choose where to save the database file"),
			initialDir,
			"database.db",
			wildcard=_("Database files (*.db)|*.db"),
			style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
		)

		try:
			if dlg.ShowModal() != wx.ID_OK:
				return

			newPath = dlg.GetPath()
			currentIndex = self.pathNameCB.GetSelection()

			if currentIndex == 0:
				self.dbConfig.firstDatabase = newPath
			elif currentIndex == 1:
				self.dbConfig.altDatabase = newPath
			else:
				return

			# Refresh the database selection control.
			self.pathNameCB.Set(self._getDatabaseChoices())
			self.pathNameCB.SetSelection(currentIndex)

		finally:
			dlg.Destroy()

	def isValid(self) -> bool:
		"""
		Validate settings before saving.
		"""
		if not self.dbConfig.firstDatabase or not self.dbConfig.firstDatabase.strip():
			wx.MessageBox(
				_("The primary database path cannot be empty."),
				_("Validation Error"),
				wx.OK | wx.ICON_ERROR,
				self,
			)
			return False

		return True

	def onSave(self):
		"""
		Save the SIRA settings.
		"""
		# Save phone field masks.
		setFormatCellPhone(self.textCellPhone.GetValue())
		setFormatLandline(self.textLandline.GetValue())

		# Save general options.
		setRemoveConfigOnUninstall(
			self.removeConfigOnUninstall.GetValue(),
		)
		setResetRecords(self.resetRecords.GetValue())
		setImportCSV(self.importCSV.GetValue())
		setExportCSV(self.exportCSV.GetValue())

		# Save the selected database.
		self.dbConfig.indexDB = self.pathNameCB.GetSelection()
		self.dbConfig.saveConfig()

# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html
"""

import os
from typing import Any, cast

import addonHandler
import config
import wx
from gui import guiHelper, mainFrame
from gui.settingsDialogs import SettingsPanel

from .dbConfig import DatabaseConfig
from .varsConfig import ADDON_NAME, ADDON_SUMMARY

# Initialize translation
addonHandler.initTranslation()


# =========================
# Settings Panel
# =========================


class SIRASystemSettingsPanel(SettingsPanel):
	# Translators: Title of the add-on settings panel
	title = ADDON_SUMMARY

	def makeSettings(self, sizer):
		settingsSizerHelper = guiHelper.BoxSizerHelper(self, sizer=sizer)

		# Materialize configuration safely
		conf = config.conf.get(ADDON_NAME)
		if conf is None:
			conf = config.conf[ADDON_NAME]

		# Initialize database config lazily
		self.db_config = DatabaseConfig(
			default_path=os.path.join(os.path.dirname(__file__), "database.db"),
		)
		self.db_config.load_config()

		# =========================
		# Phone formatting
		# =========================

		phoneBoxSizer = wx.StaticBoxSizer(
			wx.HORIZONTAL,
			self,
			label=_("Add mask for phone fields:"),
		)
		phoneBox = phoneBoxSizer.GetStaticBox()
		phoneGroup = guiHelper.BoxSizerHelper(self, sizer=phoneBoxSizer)
		settingsSizerHelper.addItem(phoneGroup)

		# Cell phone
		wx.StaticText(phoneBox, label=_("Cell phone"))
		self.textCellPhone = wx.TextCtrl(phoneBox)
		self.textCellPhone.SetValue(conf.get("formatCellPhone", "(##) #####-####"))

		# Landline
		wx.StaticText(phoneBox, label=_("Landline"))
		self.textLandline = wx.TextCtrl(phoneBox)
		self.textLandline.SetValue(conf.get("formatLandline", "(##) ####-####"))

		# =========================
		# Options
		# =========================

		self.removeConfigOnUninstall = wx.CheckBox(
			self,
			label=_("Remove all saved settings when uninstalling this add-on"),
		)
		self.removeConfigOnUninstall.SetValue(
			bool(conf.get("removeConfigOnUninstall", False)),
		)
		settingsSizerHelper.addItem(self.removeConfigOnUninstall)

		self.resetRecords = wx.CheckBox(
			self,
			label=_("Show option to delete entire calendar"),
		)
		self.resetRecords.SetValue(
			bool(conf.get("resetRecords", True)),
		)
		settingsSizerHelper.addItem(self.resetRecords)

		self.importCSV = wx.CheckBox(
			self,
			label=_("Show import CSV file button"),
		)
		self.importCSV.SetValue(
			bool(conf.get("importCSV", True)),
		)
		settingsSizerHelper.addItem(self.importCSV)

		self.exportCSV = wx.CheckBox(
			self,
			label=_("Show export CSV file button"),
		)
		self.exportCSV.SetValue(
			bool(conf.get("exportCSV", True)),
		)
		settingsSizerHelper.addItem(self.exportCSV)

		# =========================
		# Database path selection
		# =========================

		pathBoxSizer = wx.StaticBoxSizer(
			wx.HORIZONTAL,
			self,
			label=_("Path of agenda files:"),
		)
		pathBox = pathBoxSizer.GetStaticBox()
		pathGroup = guiHelper.BoxSizerHelper(self, sizer=pathBoxSizer)
		settingsSizerHelper.addItem(pathGroup)

		self.pathList = [
			self.db_config.first_database,
			self.db_config.alt_database,
		]
		self.pathNameCB = pathGroup.addLabeledControl(
			"",
			wx.Choice,
			choices=self.pathList,
		)
		self.pathNameCB.SetSelection(self.db_config.index_db)

		changePathBtn = wx.Button(
			pathBox,
			label=_("&Select or add a directory"),
		)
		changePathBtn.Bind(wx.EVT_BUTTON, self.onSelectDirectory)

	# =========================
	# Handlers
	# =========================

	def onSelectDirectory(self, event):
		dlg = wx.FileDialog(
			mainFrame,
			_("Choose where to save the database file"),
			os.path.dirname(__file__),
			"database.db",
			wildcard=_("Database files (*.db)"),
			style=wx.FD_SAVE,
		)

		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			self.db_config.index_db = self.pathNameCB.GetSelection()
			self.db_config.update_database_path(path)

			self.pathList = [
				self.db_config.first_database,
				self.db_config.alt_database,
			]
			self.pathNameCB.Set(self.pathList)
			self.pathNameCB.SetSelection(self.db_config.index_db)

		dlg.Destroy()

	# =========================
	# Save
	# =========================

	def onSave(self):
		conf = config.conf.get(ADDON_NAME)
		if ADDON_NAME not in config.conf:
			config.conf[ADDON_NAME] = {}

		conf = cast(dict[str, Any], config.conf[ADDON_NAME])

		conf["formatCellPhone"] = self.textCellPhone.GetValue()
		conf["formatLandline"] = self.textLandline.GetValue()
		conf["removeConfigOnUninstall"] = self.removeConfigOnUninstall.GetValue()
		conf["resetRecords"] = self.resetRecords.GetValue()
		conf["importCSV"] = self.importCSV.GetValue()
		conf["exportCSV"] = self.exportCSV.GetValue()

		self.db_config.index_db = self.pathNameCB.GetSelection()
		self.db_config.save_config()

		config.conf.enableProfileTriggers()

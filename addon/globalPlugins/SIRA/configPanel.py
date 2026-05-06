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
from typing import Any, cast
from pathlib import Path

import addonHandler
import config
import globalVars
import wx
from gui import guiHelper
from gui.settingsDialogs import SettingsPanel

from .dbConfig import DatabaseConfig
from .varsConfig import ADDON_NAME, ADDON_SUMMARY

# Initialize translation
addonHandler.initTranslation()


class SIRASystemSettingsPanel(SettingsPanel):
	title = ADDON_SUMMARY

	def makeSettings(self, sizer):
		settingsSizerHelper = guiHelper.BoxSizerHelper(self, sizer=sizer)

		# Garantir que a configuração existe
		if ADDON_NAME not in config.conf:
			config.conf[ADDON_NAME] = {}
		conf = config.conf[ADDON_NAME]

		# Inicializa a configuração da base de dados
		self.dbConfig = DatabaseConfig(
			defaultPath=Path(globalVars.appArgs.configPath) / "SIRA_DB" / "database.db",
		)
		self.dbConfig.loadConfig()

		# --- GRUPO 1: Máscaras de Telefone ---
		phoneBoxSizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=_("Phone field masks:"))
		phoneGrid = wx.FlexGridSizer(cols=2, vgap=10, hgap=10)

		phoneGrid.Add(
			wx.StaticText(phoneBoxSizer.GetStaticBox(), label=_("Cell phone:")),
			0,
			wx.ALIGN_CENTER_VERTICAL,
		)
		self.textCellPhone = wx.TextCtrl(phoneBoxSizer.GetStaticBox())
		self.textCellPhone.SetValue(conf.get("formatCellPhone", "(##) #####-####"))
		phoneGrid.Add(self.textCellPhone, 1, wx.EXPAND)

		phoneGrid.Add(
			wx.StaticText(phoneBoxSizer.GetStaticBox(), label=_("Landline:")),
			0,
			wx.ALIGN_CENTER_VERTICAL,
		)
		self.textLandline = wx.TextCtrl(phoneBoxSizer.GetStaticBox())
		self.textLandline.SetValue(conf.get("formatLandline", "(##) ####-####"))
		phoneGrid.Add(self.textLandline, 1, wx.EXPAND)

		phoneBoxSizer.Add(phoneGrid, 1, wx.ALL | wx.EXPAND, 10)
		settingsSizerHelper.addItem(phoneBoxSizer)

		# --- GRUPO 2: Opções Gerais ---
		optionsBoxSizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=_("General Options:"))
		optionsBox = optionsBoxSizer.GetStaticBox()

		self.removeConfigOnUninstall = wx.CheckBox(optionsBox, label=_("Remove settings on uninstall"))
		self.removeConfigOnUninstall.SetValue(bool(conf.get("removeConfigOnUninstall", False)))

		self.resetRecords = wx.CheckBox(optionsBox, label=_("Show option to delete entire calendar"))
		self.resetRecords.SetValue(bool(conf.get("resetRecords", True)))

		self.importCSV = wx.CheckBox(optionsBox, label=_("Show import CSV button"))
		self.importCSV.SetValue(bool(conf.get("importCSV", True)))

		self.exportCSV = wx.CheckBox(optionsBox, label=_("Show export CSV button"))
		self.exportCSV.SetValue(bool(conf.get("exportCSV", True)))

		for cb in (self.removeConfigOnUninstall, self.resetRecords, self.importCSV, self.exportCSV):
			optionsBoxSizer.Add(cb, 0, wx.ALL, 5)
		settingsSizerHelper.addItem(optionsBoxSizer)

		# --- GRUPO 3: Localização dos Dados ---
		pathBoxSizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=_("Database Management:"))

		# Prepara a lista para o Choice, lidando com strings vazias
		displayPaths = [
			self.dbConfig.firstDatabase,
			self.dbConfig.altDatabase if self.dbConfig.altDatabase else _("Empty (Not configured)"),
		]

		pathGroupHelper = guiHelper.BoxSizerHelper(self, sizer=pathBoxSizer)
		self.pathNameCB = pathGroupHelper.addLabeledControl(
			_("Current database path:"),
			wx.Choice,
			choices=displayPaths,
		)
		self.pathNameCB.SetSelection(self.dbConfig.indexDB)

		self.changePathBtn = wx.Button(pathBoxSizer.GetStaticBox(), label=_("&Select or add a directory"))
		self.changePathBtn.Bind(wx.EVT_BUTTON, self.onSelectDirectory)
		pathBoxSizer.Add(self.changePathBtn, 0, wx.ALL | wx.CENTER, 5)

		settingsSizerHelper.addItem(pathBoxSizer)

	def onSelectDirectory(self, event):
		# Define o diretório atual para abrir o diálogo na pasta certa
		currentPath = self.dbConfig.getCurrentDatabasePath()
		initialDir = os.path.dirname(str(currentPath)) if currentPath else os.path.expanduser("~")

		dlg = wx.FileDialog(
			self,  # Usar self (o painel) como pai é mais seguro
			_("Choose where to save the database file"),
			initialDir,
			"database.db",
			wildcard=_("Database files (*.db)|*.db"),
			style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
		)

		if dlg.ShowModal() == wx.ID_OK:
			newPath = dlg.GetPath()
			currentIndex = self.pathNameCB.GetSelection()

			# ATENÇÃO: Corrigindo a lógica de atualização do caminho
			if currentIndex == 0:
				self.dbConfig.firstDatabase = newPath
			else:
				self.dbConfig.altDatabase = newPath

			# Atualiza a interface
			displayPaths = [
				self.dbConfig.firstDatabase,
				self.dbConfig.altDatabase,
			]
			self.pathNameCB.Set(displayPaths)
			self.pathNameCB.SetSelection(currentIndex)

		dlg.Destroy()

	def isValid(self) -> bool:
		"""
		Validates that the settings are correct before allowing saving.
		"""

		# Basic validation: the primary database path cannot be empty
		if not self.dbConfig.firstDatabase:
			wx.MessageBox(
				_("The primary database path cannot be empty."),
				_("Validation Error"),
				wx.OK | wx.ICON_ERROR,
				self,
			)
			return False

		return True  # All right, you can save!

	def onSave(self):
		conf = cast(dict[str, Any], config.conf[ADDON_NAME])

		conf["formatCellPhone"] = self.textCellPhone.GetValue()
		conf["formatLandline"] = self.textLandline.GetValue()
		conf["removeConfigOnUninstall"] = self.removeConfigOnUninstall.GetValue()
		conf["resetRecords"] = self.resetRecords.GetValue()
		conf["importCSV"] = self.importCSV.GetValue()
		conf["exportCSV"] = self.exportCSV.GetValue()

		# Atualiza o índice selecionado antes de salvar
		self.dbConfig.indexDB = self.pathNameCB.GetSelection()
		self.dbConfig.saveConfig()

		# Effectively saves to the nvda.ini file
		config.conf.save()

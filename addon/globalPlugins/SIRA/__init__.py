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

from functools import partial

import addonHandler
import core
import globalPluginHandler
import globalVars
import gui
import inputCore
import tones
import ui
import wx
from logHandler import log
from scriptHandler import script

from .configPanel import SIRASystemSettingsPanel
from .generalMessage import GeneralMessage
from .main import SIRA
from .medicalDischarge import MedicalDischarge
from .messageForTransport import MessageForTransport
from .model import Section
from .updateManager import UpdateManager
from .varsConfig import ADDON_NAME, ADDON_SUMMARY, ADDON_DESCRIPTION, ADDON_VERSION, initConfiguration

# Initialize translation support
addonHandler.initTranslation()

GITHUB_REPO = f"EdilbertoFonseca/{ADDON_NAME}"


# Secure mode decorator
def disableInSecureMode(decoratedCls):
	if globalVars.appArgs.secure:
		return globalPluginHandler.GlobalPlugin
	return decoratedCls


@disableInSecureMode
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super().__init__()
		log.info(f"{ADDON_NAME} {ADDON_VERSION} initializing")

		# Ensure configuration is initialized
		initConfiguration()

		# Inicialização tardia (evita efeitos colaterais no import)
		try:
			Section.initDB()
		except Exception as e:
			log.error(f"Database initialization failed: {e}")

		self.updateManager = UpdateManager(
			repoName=GITHUB_REPO,
			currentVersion=ADDON_VERSION,
			addonNameForFile=ADDON_NAME,
		)

		self._registerSettingsPanel()
		self._createMenu()
		self.isLayerActive = False

	# Settings panel
	def _registerSettingsPanel(self):
		classes = gui.settingsDialogs.NVDASettingsDialog.categoryClasses
		if SIRASystemSettingsPanel not in classes:
			classes.append(SIRASystemSettingsPanel)

	# Menu creation

	def _createMenu(self):
		self.toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu
		self.mainMenu = wx.Menu()

		self.menuList = self.mainMenu.Append(
			wx.ID_ANY,
			_("&Lists of registered extensions..."),
		)
		self.menuTransport = self.mainMenu.Append(
			wx.ID_ANY,
			_("Message for &transport..."),
		)
		self.menuMedical = self.mainMenu.Append(
			wx.ID_ANY,
			_("Medical discharge &register..."),
		)
		self.menuGeneral = self.mainMenu.Append(
			wx.ID_ANY,
			_("&General message..."),
		)

		self.mainMenu.AppendSeparator()

		self.menuUpdate = self.mainMenu.Append(
			wx.ID_ANY,
			_("Check for &updates..."),
		)
		self.menuSettings = self.mainMenu.Append(
			wx.ID_ANY,
			_("&Settings..."),
		)
		self.menuHelp = self.mainMenu.Append(
			wx.ID_ANY,
			_("&Help"),
		)

		# Bindings (handlers dedicados, não scripts)
		icon = gui.mainFrame.sysTrayIcon
		icon.Bind(wx.EVT_MENU, self.script_openList, self.menuList)
		icon.Bind(wx.EVT_MENU, self.script_openTransport, self.menuTransport)
		icon.Bind(wx.EVT_MENU, self.script_openMedical, self.menuMedical)
		icon.Bind(wx.EVT_MENU, self.script_openGeneral, self.menuGeneral)
		icon.Bind(wx.EVT_MENU, self._onCheckUpdates, self.menuUpdate)
		icon.Bind(wx.EVT_MENU, self._onOpenSettings, self.menuSettings)
		icon.Bind(wx.EVT_MENU, self._onHelp, self.menuHelp)

		self.menuItem = self.toolsMenu.AppendSubMenu(
			self.mainMenu,
			"&{}...".format(ADDON_SUMMARY),
		)

	def _onCheckUpdates(self, event):
		self.updateManager.checkForUpdates(silent=False)

	def _onOpenSettings(self, event):
		def _open_settings():
			method = getattr(gui.mainFrame, "popupSettingsDialog", None)
			if callable(method):
				method(gui.settingsDialogs.NVDASettingsDialog, SIRASystemSettingsPanel)
			else:
				log.warning("popupSettingsDialog not available on mainFrame")

		wx.CallAfter(_open_settings)

	def _onHelp(self, event):
		try:
			addon = addonHandler.getCodeAddon()

			if not addon:
				log.warning("Addon not found for help")
				ui.message(_("Help not available"))
				return

			docPath = addon.getDocFilePath()

			if not docPath:
				log.warning("Documentation file not found")
				ui.message(_("Help not available"))
				return

			wx.LaunchDefaultBrowser(docPath)

		except Exception as e:
			log.error(f"Error opening help: {e}")
			ui.message(_("Error opening help"))

	# Layer Logic (Layered Gestures)

	@script(
		gesture="kb:nvda+shift+r",
		description="{addon}".format(addon=ADDON_DESCRIPTION),
		category=ADDON_SUMMARY,
	)
	def script_siraLayer(self, gesture):
		if self.isLayerActive:
			return

		self.isLayerActive = True
		tones.beep(880, 100)

		# Capture the next key
		inputCore.manager._captureFunc = self._handleLayerInput  # pyright: ignore[reportPrivateUsage]

		# 5 second timeout
		core.callLater(5000, self._cancelLayer)

	def _handleLayerInput(self, gesture):
		try:
			key = gesture.mainKeyName

			if not key:
				return False

			key = key.lower()

			if key == "l":
				wx.CallAfter(self.script_openList, None)

			elif key == "t":
				wx.CallAfter(self.script_openTransport, None)

			elif key == "m":
				wx.CallAfter(self.script_openMedical, None)

			elif key == "g":
				wx.CallAfter(self.script_openGeneral, None)

			elif key == "u":
				wx.CallAfter(self.script_update, None)

			elif key == "h":
				wx.CallAfter(self.script_help, None)

			elif key == "c":
				wx.CallAfter(self.script_siraConfig, None)

			elif key == "escape":
				ui.message(_("Canceled layer"))

			else:
				ui.message(_("Key {} not defined").format(key))

		except Exception as e:
			log.error(f"Layer error: {e}")

		finally:
			self._finishLayer()

		return False

	def _cancelLayer(self):
		"""Cancels the layer due to timeout."""
		if self.isLayerActive:
			ui.message(_("Expired layer"))
			self._finishLayer()

	def _finishLayer(self):
		"""Finishes the layer safely."""
		inputCore.manager._captureFunc = None  # pyright: ignore[reportPrivateUsage]
		self.isLayerActive = False
		tones.beep(440, 50)

	def script_openList(self, gesture):
		wx.CallAfter(self.displayDialog, SIRA, "dlgSIRA", _("Lists of registered extensions"))

	def script_openTransport(self, gesture):
		wx.CallAfter(self.displayDialog, MessageForTransport, "dlgTransport", _("Message for transport"))

	def script_openMedical(self, gesture):
		wx.CallAfter(self.displayDialog, MedicalDischarge, "dlgMedical", _("Medical discharge register"))

	def script_openGeneral(self, gesture):
		wx.CallAfter(self.displayDialog, GeneralMessage, "dlgGeneral", _("General message"))

	def script_update(self, gesture):
		self._onCheckUpdates(None)

	def script_help(self, gesture):
		self._onHelp(None)

	def script_siraConfig(self, gesture):
		def _open_settings():
			method = getattr(gui.mainFrame, "popupSettingsDialog", None)
			if callable(method):
				method(
					gui.settingsDialogs.NVDASettingsDialog,
					SIRASystemSettingsPanel,
				)
			else:
				log.warning("popupSettingsDialog not available")

		wx.CallAfter(_open_settings)

	def _onDestroy(self, e: wx.Event, attrName: str) -> None:
		self.onGenericClosed(e, attrName)

	def displayDialog(self, dialogClass, attrName, *args, **kwargs):
		# 1. Retrieves what is stored in the attribute
		dlg = getattr(self, attrName, None)

		# 2. "Life" check:
		# If None OR if the wx object is no longer valid (window closed)
		if dlg is None or not dlg:
			# We create a new instance
			dlg = dialogClass(gui.mainFrame, *args, **kwargs)
			setattr(self, attrName, dlg)

			# We bind the attribute cleanup when the window is destroyed
			dlg.Bind(wx.EVT_WINDOW_DESTROY, partial(self._onDestroy, attrName=attrName))

		# 3. Display and Focus
		try:
			gui.mainFrame.prePopup()

			# We check once again if the object is active before calling methods
			if dlg:
				if dlg.IsIconized():
					dlg.Restore()
				dlg.Show()
				dlg.Raise()
				dlg.SetFocus()

			gui.mainFrame.postPopup()
		except Exception as e:
			log.error(f"Error when manipulating window {attrName}: {e}")
			setattr(self, attrName, None)

	def onGenericClosed(self, evt: wx.Event, attrName: str) -> None:
		"""Handles the closure of generic dialogs."""
		setattr(self, attrName, None)
		evt.Skip()

	def terminate(self):
		"""Terminates the SIRA addon."""
		super().terminate()

		try:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(
				SIRASystemSettingsPanel,
			)
		except ValueError:
			pass

		try:
			self.toolsMenu.Remove(self.menuItem)
		except Exception as e:
			log.warning(f"Failed to remove menu: {e}")

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

		self.isLayerActive = False
		self._layerGeneration = 0
		self._layerGestures = (
			"kb:l",
			"kb:t",
			"kb:m",
			"kb:g",
			"kb:u",
			"kb:h",
			"kb:c",
			"kb:d",
			"kb:escape",
		)

		self._registerSettingsPanel()
		self._createMenu()

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
		def _openSettings():
			method = getattr(gui.mainFrame, "popupSettingsDialog", None)
			if callable(method):
				method(gui.settingsDialogs.NVDASettingsDialog, SIRASystemSettingsPanel)
			else:
				log.warning("popupSettingsDialog not available on mainFrame")

		wx.CallAfter(_openSettings)

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

	# Layer Logic (Layered Gestures)

	@script(
		gesture="kb:nvda+shift+r",
		description="{addon}".format(addon=ADDON_DESCRIPTION),
		category=ADDON_SUMMARY,
	)
	def script_siraLayer(self, gesture):
		"""Activates the temporary command layer."""
		if self.isLayerActive:
			return

		self.isLayerActive = True
		self._layerGeneration += 1
		generation = self._layerGeneration

		try:
			for gestureIdentifier in self._layerGestures:
				self.bindGesture(gestureIdentifier, "layerCommand")

			tones.beep(880, 100)
			core.callLater(
				5000,
				partial(self._cancelLayer, generation),
			)

		except Exception:
			log.exception("Failed to activate command layer")
			self._finishLayer()
			ui.message(_("Unable to activate command layer"))

	def script_layerCommand(self, gesture):
		"""Processes a command received while the layer is active."""
		if not self.isLayerActive:
			return

		key = gesture.mainKeyName

		if not key:
			return

		key = key.lower()

		commands = {
			"l": self.script_openList,
			"t": self.script_openTransport,
			"m": self.script_openMedical,
			"g": self.script_openGeneral,
			"u": self.script_update,
			"c": self.script_siraConfig,
			"d": self.script_help,
		}

		# Finish the layer before executing the selected command.
		self._finishLayer()

		if key == "escape":
			ui.message(_("Canceled layer"))
			return

		if key == "h":
			msg = _("""Press L to open the registered extensions list.
Press T to save a message for transport.
Press M to save a medical discharge record.
Press G to save a general message.
Press U to check for updates.
Press C to open settings.
Press D to open the documentation.
Press H to open the shortcut help.
Press Escape to cancel the layer.""")

			ui.browseableMessage(
				msg,
				_("Command layer help. "),
				closeButton=True,
			)
			return

		command = commands.get(key)

		if command:
			wx.CallAfter(command, None)

	def _cancelLayer(self, generation):
		"""Cancels the layer if its timeout has expired."""
		if not self.isLayerActive:
			return

		if generation != self._layerGeneration:
			return

		self._finishLayer()
		ui.message(_("Expired layer"))

	def _finishLayer(self):
		"""Removes temporary gesture bindings and finishes the layer."""
		if not self.isLayerActive:
			return

		for gestureIdentifier in self._layerGestures:
			try:
				self.removeGestureBinding(gestureIdentifier)
			except LookupError:
				pass

		self.isLayerActive = False
		self._layerGeneration += 1

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
		def _openSettings():
			method = getattr(gui.mainFrame, "popupSettingsDialog", None)
			if callable(method):
				method(
					gui.settingsDialogs.NVDASettingsDialog,
					SIRASystemSettingsPanel,
				)
			else:
				log.warning("popupSettingsDialog not available")

		wx.CallAfter(_openSettings)

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

	def captureFunc(self):
		# Lógica ou apenas o retorno da função interna
		return self._captureFunc()

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

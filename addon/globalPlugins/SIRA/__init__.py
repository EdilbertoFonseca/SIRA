# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

Created on: 25/02/2025
"""

import os

import addonHandler
import globalPluginHandler
import globalVars
import gui
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
from .varsConfig import ADDON_NAME, ADDON_SUMMARY, ADDON_VERSION, initConfiguration

# Initialize translation support
addonHandler.initTranslation()

GITHUB_REPO = f"EdilbertoFonseca/{ADDON_NAME}"

# =========================
# Secure mode decorator
# =========================


def disableInSecureMode(decoratedCls):
	if globalVars.appArgs.secure:
		return globalPluginHandler.GlobalPlugin
	return decoratedCls


# =========================
# Global Plugin
# =========================


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
			reponame=GITHUB_REPO,
			currentversion=ADDON_VERSION,
			addonnameforfile=ADDON_NAME,
		)

		self._registerSettingsPanel()
		self._createMenu()

	# =========================
	# Settings panel
	# =========================

	def _registerSettingsPanel(self):
		classes = gui.settingsDialogs.NVDASettingsDialog.categoryClasses
		if SIRASystemSettingsPanel not in classes:
			classes.append(SIRASystemSettingsPanel)

	# =========================
	# Menu creation
	# =========================

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
		icon.Bind(wx.EVT_MENU, self._onList, self.menuList)
		icon.Bind(wx.EVT_MENU, self._onTransport, self.menuTransport)
		icon.Bind(wx.EVT_MENU, self._onMedical, self.menuMedical)
		icon.Bind(wx.EVT_MENU, self._onGeneral, self.menuGeneral)
		icon.Bind(wx.EVT_MENU, self._onCheckUpdates, self.menuUpdate)
		icon.Bind(wx.EVT_MENU, self._onOpenSettings, self.menuSettings)
		icon.Bind(wx.EVT_MENU, self._onHelp, self.menuHelp)

		self.menuItem = self.toolsMenu.AppendSubMenu(
			self.mainMenu,
			"&{}...".format(ADDON_SUMMARY),
		)

	# =========================
	# Menu handlers (GUI thread)
	# =========================

	def _popup(self, dlg):
		gui.mainFrame.prePopup()
		dlg.CentreOnScreen()
		dlg.ShowModal()
		gui.mainFrame.postPopup()

	def _onList(self, event):
		wx.CallAfter(
			self._popup,
			SIRA(gui.mainFrame, _("Lists of registered extensions")),
		)

	def _onTransport(self, event):
		wx.CallAfter(
			self._popup,
			MessageForTransport(gui.mainFrame, _("Message for transport")),
		)

	def _onMedical(self, event):
		wx.CallAfter(
			self._popup,
			MedicalDischarge(gui.mainFrame, _("Medical discharge register")),
		)

	def _onGeneral(self, event):
		wx.CallAfter(
			self._popup,
			GeneralMessage(gui.mainFrame, _("General message")),
		)

	def _onCheckUpdates(self, event):
		self.updateManager.checkforupdates(silent=False)

	def _onOpenSettings(self, event):
		def _open_settings():
			method = getattr(gui.mainFrame, "popupSettingsDialog", None)
			if callable(method):
				method(gui.settingsDialogs.NVDASettingsDialog, SIRASystemSettingsPanel)
			else:
				log.warning("popupSettingsDialog not available on mainFrame")

		wx.CallAfter(_open_settings)

	def _onHelp(self, event):
		wx.LaunchDefaultBrowser(
			addonHandler.Addon(
				os.path.join(os.path.dirname(__file__), "..", ".."),
			).getDocFilePath(),
		)

	# =========================
	# NVDA scripts (keyboard)
	# =========================

	@script(
		gesture="kb:Alt+numpad1",
		description=_(
			"{addon} - Opens the list of registered extensions.",
		).format(addon=ADDON_NAME),
		category=ADDON_SUMMARY,
	)
	def script_openList(self, gesture):
		self._onList(None)

	@script(
		gesture="kb:Alt+numpad2",
		description=_(
			"{addon} - Opens the message for transport dialog.",
		).format(addon=ADDON_NAME),
		category=ADDON_SUMMARY,
	)
	def script_openTransport(self, gesture):
		self._onTransport(None)

	@script(
		gesture="kb:Alt+numpad3",
		description=_(
			"{addon} - Opens the medical discharge register.",
		).format(addon=ADDON_NAME),
		category=ADDON_SUMMARY,
	)
	def script_openMedical(self, gesture):
		self._onMedical(None)

	@script(
		gesture="kb:Alt+numpad4",
		description=_(
			"{addon} - Opens the general message dialog.",
		).format(addon=ADDON_NAME),
		category=ADDON_SUMMARY,
	)
	def script_openGeneral(self, gesture):
		self._onGeneral(None)

	@script(
		gesture="kb:Alt+numpad5",
		description=_(
			"{addon} - Check for updates.",
		).format(addon=ADDON_NAME),
		category=ADDON_SUMMARY,
	)
	def script_update(self, gesture):
		self._onCheckUpdates(None)

	# =========================
	# Cleanup
	# =========================

	def terminate(self):
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

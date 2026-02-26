# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

Created on: 15/12/2025
"""

import json
import os
import re
import tempfile
import threading
import urllib.error
import urllib.request

import addonHandler
import gui
import ui
import wx
from logHandler import log

# Initialize translation support
addonHandler.initTranslation()


class UpdateManager:
	"""
	Gerencia a verificação e instalação de atualizações do add-on via GitHub.
	"""

	def __init__(self, reponame, currentversion, addonnameforfile):
		super().__init__()
		self.reponame = reponame
		self.currentversion = currentversion
		self.addonnameforfile = addonnameforfile

		self.latestversion = None
		self.downloadurl = None
		self.changes = None

		log.info(
			f"UpdateManager initialized for {self.reponame}, current version {self.currentversion}",
		)

	# PUBLIC API
	def checkforupdates(self, silent=True):
		"""
		Inicia a verificação de atualizações em thread separada.
		"""
		threading.Thread(
			target=self._checkthread,
			args=(silent,),
			daemon=True,
		).start()

	# ============================
	# INTERNAL METHODS
	# ============================

	def _checkthread(self, silent):
		try:
			url = f"https://api.github.com/repos/{self.reponame}/releases/latest"

			req = urllib.request.Request(
				url,
				headers={"User-Agent": "NVDA-Addon-UpdateManager"},
			)

			with urllib.request.urlopen(req) as response:
				data = json.loads(response.read().decode("utf-8"))

			self.latestversion = data.get("tag_name", "").lstrip("vV")

			if not self.latestversion:
				raise ValueError("Invalid version information received")

			log.info(f"Latest version found: {self.latestversion}")

			if self._compareversions(self.latestversion, self.currentversion) <= 0:
				if not silent:
					wx.CallAfter(
						ui.message,
						_("You are already running the latest version of SIRA."),
					)
				return

			self.changes = data.get("body", _("No release notes provided."))

			self.downloadurl = self._find_addon_asset(data)

			if not self.downloadurl:
				log.warning("No .nvda-addon file found in release assets.")
				if not silent:
					wx.CallAfter(
						ui.message,
						_("An update is available, but no add-on file was found."),
					)
				return

			wx.CallAfter(
				self._promptupdate,
				self.latestversion,
				self.downloadurl,
				self.changes,
			)

		except urllib.error.URLError as e:
			log.error(f"Network error while checking updates: {e}")
			if not silent:
				wx.CallAfter(
					ui.message,
					_("Failed to check for updates due to a network error."),
				)

		except Exception as e:
			log.error(
				f"Unexpected error while checking updates: {e}",
				excinfo=True,  # pyright: ignore[reportCallIssue]
			)
			if not silent:
				wx.CallAfter(
					ui.message,
					_("An unexpected error occurred while checking for updates."),
				)

	def _find_addon_asset(self, data):
		for asset in data.get("assets", []):
			name = asset.get("name", "")
			if name.endswith(".nvda-addon"):
				return asset.get("browser_download_url")
		return None

	def _compareversions(self, v1, v2):
		def normalize(v):
			return [int(x) for x in re.sub(r"(\.0+)$", "", v).split(".")]

		return (normalize(v1) > normalize(v2)) - (normalize(v1) < normalize(v2))

	# ============================
	# UI METHODS (MAIN THREAD)
	# ============================

	def _promptupdate(self, version, url, changes):
		title = _("Update available for {addon}").format(
			addon=self.addonnameforfile,
		)

		message = _(
			"A new version of {addon} ({version}) is available.\n\n"
			+ "Changes:\n{changes}\n\n"
			+ "Do you want to download and install it now?",
		).format(
			addon=self.addonnameforfile,
			version=version,
			changes=changes,
		)

		if gui.messageBox(message, title, wx.YES | wx.NO | wx.ICON_INFORMATION) == wx.YES:
			threading.Thread(
				target=self._downloadinstallthread,
				args=(url,),
				daemon=True,
			).start()

	def _downloadinstallthread(self, url):
		try:
			wx.CallAfter(
				ui.message,
				_("Downloading update for {addon}...").format(
					addon=self.addonnameforfile,
				),
			)

			tempdir = tempfile.mkdtemp(prefix="nvdaAddonUpdate_")
			addonpath = os.path.join(
				tempdir,
				f"{self.addonnameforfile}.nvda-addon",
			)

			req = urllib.request.Request(
				url,
				headers={"User-Agent": "NVDA-Addon-UpdateManager"},
			)

			with urllib.request.urlopen(req) as response, open(addonpath, "wb") as f:
				f.write(response.read())

			log.info(f"Add-on downloaded to {addonpath}")

			wx.CallAfter(
				ui.message,
				_("Installing update for {addon}...").format(
					addon=self.addonnameforfile,
				),
			)

			os.startfile(addonpath)

			# Não removemos o arquivo imediatamente.
			# O NVDA pode ainda precisar dele durante a instalação.

		except urllib.error.URLError as e:
			log.error(f"Download error: {e}")
			wx.CallAfter(
				ui.message,
				_("Failed to download the update due to a network error."),
			)

		except Exception as e:
			log.error(f"Unexpected error during download/install: {e}")
			wx.CallAfter(
				ui.message,
				_("An unexpected error occurred while installing the update."),
			)

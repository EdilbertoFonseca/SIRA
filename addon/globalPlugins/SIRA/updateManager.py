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
	Manages checking and installing add-on updates via GitHub.
	"""

	def __init__(self, repoName, currentVersion, addonNameForFile):
		super().__init__()
		self.repoName = repoName
		self.currentVersion = currentVersion
		self.addonNameForFile = addonNameForFile

		self.latestVersion = None
		self.downloadURL = None
		self.changes = None

		log.info(
			f"UpdateManager initialized for {self.repoName}, current version {self.currentVersion}",
		)

	# PUBLIC API
	def checkForUpdates(self, silent=True):
		"""
		Starts checking for updates in a separate thread.
		"""
		threading.Thread(
			target=self._checkThread,
			args=(silent,),
			daemon=True,
		).start()

	# INTERNAL METHODS

	def _checkThread(self, silent):
		try:
			url = f"https://api.github.com/repos/{self.repoName}/releases/latest"

			req = urllib.request.Request(
				url,
				headers={"User-Agent": "NVDA-Addon-UpdateManager"},
			)

			with urllib.request.urlopen(req) as response:
				data = json.loads(response.read().decode("utf-8"))

			self.latestVersion = data.get("tag_name", "").lstrip("vV")

			if not self.latestVersion:
				raise ValueError("Invalid version information received")

			log.info(f"Latest version found: {self.latestVersion}")

			if self._compareVersions(self.latestVersion, self.currentVersion) <= 0:
				if not silent:
					wx.CallAfter(
						ui.message,
						_(
							"You are already running the latest version of SIRA - {}.".format(
								self.currentVersion,
							),
						),
					)
				return

			self.changes = data.get("body", _("No release notes provided."))

			self.downloadURL = self._findAddonAsset(data)

			if not self.downloadURL:
				log.warning("No .nvda-addon file found in release assets.")
				if not silent:
					wx.CallAfter(
						ui.message,
						_("An update is available, but no add-on file was found."),
					)
				return

			wx.CallAfter(
				self._promptUpdate,
				self.latestVersion,
				self.downloadURL,
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
			log.error(f"Unexpected error while checking updates: {e}", exc_info=True)

			if not silent:
				wx.CallAfter(
					ui.message,
					_("An unexpected error occurred while checking for updates."),
				)

	def _findAddonAsset(self, data):
		for asset in data.get("assets", []):
			name = asset.get("name", "")
			if name.endswith(".nvda-addon"):
				return asset.get("browser_download_url")
		return None

	def _compareVersions(self, v1, v2):
		def normalize(v):
			return [int(x) for x in re.sub(r"(\.0+)$", "", v).split(".")]

		return (normalize(v1) > normalize(v2)) - (normalize(v1) < normalize(v2))

	# UI METHODS (MAIN THREAD)

	def _promptUpdate(self, version, url, changes):
		title = _("Update available for {addon}").format(
			addon=self.addonNameForFile,
		)

		message = _(
			"A new version of {addon} ({version}) is available.\n\n"
			+ "Changes:\n{changes}\n\n"
			+ "Do you want to download and install it now?",
		).format(
			addon=self.addonNameForFile,
			version=version,
			changes=changes,
		)

		if gui.messageBox(message, title, wx.YES | wx.NO | wx.ICON_INFORMATION) == wx.YES:
			threading.Thread(
				target=self._downloadInstallThread,
				args=(url,),
				daemon=True,
			).start()

	def _downloadInstallThread(self, url):
		try:
			wx.CallAfter(
				ui.message,
				_("Downloading update for {addon}...").format(
					addon=self.addonNameForFile,
				),
			)

			tempDir = tempfile.mkdtemp(prefix="nvdaAddonUpdate_")
			addonPath = os.path.join(
				tempDir,
				f"{self.addonNameForFile}.nvda-addon",
			)

			req = urllib.request.Request(
				url,
				headers={"User-Agent": "NVDA-Addon-UpdateManager"},
			)

			with urllib.request.urlopen(req) as response, open(addonPath, "wb") as f:
				f.write(response.read())

			log.info(f"Add-on downloaded to {addonPath}")

			wx.CallAfter(
				ui.message,
				_("Installing update for {addon}...").format(
					addon=self.addonNameForFile,
				),
			)

			os.startfile(addonPath)

			# We do not remove the file immediately.
			# NVDA may still need it during installation.

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

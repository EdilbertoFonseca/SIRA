# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

Created on: 08/01/2026
"""

import addonHandler
import config

# Get add-on object and internal add-on name (safe for config keys)
_addon = addonHandler.getCodeAddon()
ADDON_NAME = _addon.name


def onUninstall():
	"""
	Optionally remove add-on configuration during uninstallation.
	Uses only supported NVDA configuration APIs.
	"""

	# Check user preference
	if not config.conf.get(ADDON_NAME, {}).get("resetRecords", False):
		return

	# Clear add-on configuration safely
	config.conf[ADDON_NAME] = {}
	config.conf.save()

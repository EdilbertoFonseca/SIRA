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

Created on: 08/01/2026
"""

import addonHandler
import config

# Get add-on object and internal add-on name (safe for config keys)
_addon = addonHandler.getCodeAddon()
ADDON_NAME = _addon.name


def onUninstall():
	# 1. Check if the configuration exists
	if ADDON_NAME not in config.conf:
		return

	# 2. Check user preference
	# We use direct access via square brackets to read the value
	if not config.conf[ADDON_NAME].get("removeConfigOnUninstall", False):
		return

	try:
		# 1. We remove the specification (the mold)
		if ADDON_NAME in config.conf.spec:
			del config.conf.spec[ADDON_NAME]

		# 2. Instead of iterating over keys(), we clear the section in the base object
		# O NVDA permite remover a secção do perfil atual desta forma:
		config.conf.profiles[0].pop(ADDON_NAME, None)

		# 3. We force write so that nvda.ini is updated
		config.conf.save()

	except Exception as e:
		import logHandler

		logHandler.log.error(f"Failed to remove config from {ADDON_NAME}: {e}")

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

Created on: 08/01/2025.
"""

import os
import struct

import addonHandler
import config

# Constantes
MASK_DATE = "XX/XX/XXXX"
MASK_TIME = "XX:XX"
MASK_PHONE = "(XX) XXXXX-XXXX"

# Global Constants for Regex
EMAIL_REGEX = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}$"

# Get the path to the root of the current add-on
ADDON_PATH = os.path.dirname(__file__)

# Detect architecture
IS64 = struct.calcsize("P") * 8 == 64

# Config# Get the add-on summary contained in the manifest.
ADDON_SUMMARY = addonHandler.getCodeAddon().manifest["summary"]
ADDON_DESCRIPTION = addonHandler.getCodeAddon().manifest["description"]
ADDON_VERSION = addonHandler.getCodeAddon().manifest["version"]

_addon = addonHandler.getCodeAddon()
ADDON_NAME = _addon.name


def initConfiguration():
	"""
	Initializes the configuration specification for the Contacts Manager for NVDA add-on.
	"""
	confspec = {
		"formatLandline": 'string(default="(##) ####-####")',
		"formatCellPhone": 'string(default="(##) #####-####")',
		"removeConfigOnUninstall": "boolean(default=False)",
		"resetRecords": "boolean(default=True)",
		"importCSV": "boolean(default=True)",
		"exportCSV": "boolean(default=True)",
		"path": 'string(default="")',
		"altPath": 'string(default="")',
		"databaseIndex": "integer(default=0)",
	}
	config.conf.spec[ADDON_NAME] = confspec

	if ADDON_NAME not in config.conf:
		config.conf[ADDON_NAME] = {}


# Ensure configuration is initialized
initConfiguration()

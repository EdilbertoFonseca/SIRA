# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

Created on: 08/01/2025.
"""

import os
import struct

import addonHandler
import config

# Constantes
mask_date = "XX/XX/XXXX"
mask_time = "XX:XX"
mask_phone = "(XX) XXXXX-XXXX"

# Get the path to the root of the current add-on
ADDON_PATH = os.path.dirname(__file__)

# Detect architecture
is64 = struct.calcsize("P") * 8 == 64

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

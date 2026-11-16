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
from typing import Any, Dict, cast

import addonHandler
import config

# Constants
MASK_DATE = "XX/XX/XXXX"
MASK_TIME = "XX:XX"
MASK_PHONE = "(XX) XXXXX-XXXX"

# Global constants for regex
EMAIL_REGEX = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}$"

# Get the path to the root of the current add-on
ADDON_PATH = os.path.dirname(__file__)

# Detect architecture
IS64 = struct.calcsize("P") * 8 == 64

# Add-on information
addonHandler.initTranslation()

_addon = addonHandler.getCodeAddon()

ADDON_NAME = _addon.name
ADDON_SUMMARY = _addon.manifest["summary"]
ADDON_DESCRIPTION = _addon.manifest["description"]
ADDON_VERSION = _addon.manifest["version"]


def initConfiguration():
	"""
	Initialize the configuration specification for the SIRA add-on.
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


def _getSection() -> Dict[str, Any]:
	"""
	Return the configuration section corresponding to the add-on.
	"""
	addon = addonHandler.getCodeAddon()
	return cast(Dict[str, Any], config.conf[addon.name])


# GETTERS


def getFormatLandline() -> str:
	return _getSection().get("formatLandline", "(##) ####-####")


def getFormatCellPhone() -> str:
	return _getSection().get("formatCellPhone", "(##) #####-####")


def getRemoveConfigOnUninstall() -> bool:
	return _getSection().get("removeConfigOnUninstall", False)


def getResetRecords() -> bool:
	return _getSection().get("resetRecords", True)


def getImportCSV() -> bool:
	return _getSection().get("importCSV", True)


def getExportCSV() -> bool:
	return _getSection().get("exportCSV", True)


def getDatabasePath() -> str:
	return _getSection().get("path", "")


def getAlternativeDatabasePath() -> str:
	return _getSection().get("altPath", "")


def getDatabaseIndex() -> int:
	return _getSection().get("databaseIndex", 0)


# SETTERS


def setFormatLandline(value: str):
	_getSection()["formatLandline"] = value or ""


def setFormatCellPhone(value: str):
	_getSection()["formatCellPhone"] = value or ""


def setRemoveConfigOnUninstall(value: bool):
	_getSection()["removeConfigOnUninstall"] = bool(value)


def setResetRecords(value: bool):
	_getSection()["resetRecords"] = bool(value)


def setImportCSV(value: bool):
	_getSection()["importCSV"] = bool(value)


def setExportCSV(value: bool):
	_getSection()["exportCSV"] = bool(value)


def setDatabasePath(path: str):
	_getSection()["path"] = path or ""


def setAlternativeDatabasePath(path: str):
	_getSection()["altPath"] = path or ""


def setDatabaseIndex(index: int):
	_getSection()["databaseIndex"] = int(index)


# Initialize the configuration
initConfiguration()

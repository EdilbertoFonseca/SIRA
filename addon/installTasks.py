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

# Get add-on object and internal add-on name (safe for config keys)
_addon = addonHandler.getCodeAddon()
ADDON_NAME = _addon.name

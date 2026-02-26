# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

Created on: 09/01/2026
"""

from typing import Any, cast

import config

from .varsConfig import ADDON_NAME


class DatabaseConfig:
	def __init__(self, default_path):
		super().__init__()
		self.default_path = default_path
		self.first_database = default_path
		self.alt_database = ""
		self.index_db = 0

	def load_config(self):
		conf = config.conf.get(ADDON_NAME)
		if conf is None:
			return

		self.index_db = int(conf.get("databaseIndex", 0))
		if self.index_db == 0:
			self.first_database = conf.get("path", self.default_path)
		else:
			self.alt_database = conf.get("altPath", self.default_path)

	def save_config(self):
		if ADDON_NAME not in config.conf:
			config.conf[ADDON_NAME] = {}

		conf = cast(dict[str, Any], config.conf[ADDON_NAME])

		conf["path"] = self.first_database
		conf["altPath"] = self.alt_database
		conf["databaseIndex"] = self.index_db

	def get_current_database_path(self):
		"""
		Returns the currently selected database path.
		"""
		return self.first_database if self.index_db == 0 else self.alt_database

	def reload(self):
		"""
		Reloads database paths from NVDA configuration.
		"""
		self.load_config()

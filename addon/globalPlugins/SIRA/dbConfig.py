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

Created on: 09/01/2026
"""

from typing import Any, cast

import config

from .varsConfig import ADDON_NAME


class DatabaseConfig(object):
	def __init__(self, defaultPath):
		super().__init__()
		self.defaultPath = defaultPath
		self.firstDatabase = defaultPath
		self.altDatabase = ""
		self.indexDB = 0

	def loadConfig(self):
		"""
		Reads settings from the configuration file.
		Improvement: Loads all paths to avoid stale data in memory.
		"""
		conf = config.conf.get(ADDON_NAME)
		if conf is None:
			return

		# Loads the current index (0 for main, 1 for alternative)
		self.indexDB = int(conf.get("databaseIndex", 0))

		# Always load both paths if they exist in the config
		self.firstDatabase = conf.get("path", self.defaultPath)
		self.altDatabase = conf.get("altPath", "")

	def saveConfig(self):
		"""
		Stores the current settings in the global configuration dictionary.
		"""
		if ADDON_NAME not in config.conf:
			config.conf[ADDON_NAME] = {}

		conf = cast(dict[str, Any], config.conf[ADDON_NAME])

		conf["path"] = self.firstDatabase
		conf["altPath"] = self.altDatabase
		conf["databaseIndex"] = self.indexDB
		# save the settings
		config.conf.save()

	def getCurrentDatabasePath(self) -> str:
		"""
		Retorna o caminho da base de dados atual.
		Se o caminho estiver vazio, retorna o padrão para evitar erros.
		"""
		path = self.firstDatabase if self.indexDB == 0 else self.altDatabase

		if path and path.strip():
			return str(path)

		if self.firstDatabase and self.firstDatabase.strip():
			return str(self.firstDatabase)

		raise ValueError("Nenhum caminho de banco de dados válido definido")

	def reload(self):
		"""
		Reloads the paths from the configuration.
		"""
		self.loadConfig()

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

from pathlib import Path
from typing import Union

from .varsConfig import (
	getDatabaseIndex,
	getDatabasePath,
	getAlternativeDatabasePath,
	setDatabaseIndex,
	setDatabasePath,
	setAlternativeDatabasePath,
)


class DatabaseConfig:
	def __init__(self, defaultPath: Union[str, Path]):
		"""
		Initialize the database configuration manager.

		Args:
			defaultPath: Default path to the primary database.
		"""
		super().__init__()
		self.defaultPath = str(defaultPath)
		self.firstDatabase = self.defaultPath
		self.altDatabase = ""
		self.indexDB = 0

	def loadConfig(self):
		"""
		Load database settings from the add-on configuration.
		"""
		configuredPath = getDatabasePath()
		alternativePath = getAlternativeDatabasePath()

		# Use the default path when the primary path is not configured.
		self.firstDatabase = (
			str(configuredPath) if configuredPath and str(configuredPath).strip() else self.defaultPath
		)

		self.altDatabase = str(alternativePath) if alternativePath and str(alternativePath).strip() else ""

		# Only the primary and alternative database indexes are valid.
		try:
			index = int(getDatabaseIndex())
		except (TypeError, ValueError):
			index = 0

		self.indexDB = index if index in (0, 1) else 0

	def saveConfig(self):
		"""
		Save database settings to the add-on configuration.
		"""
		setDatabasePath(self.firstDatabase)
		setAlternativeDatabasePath(self.altDatabase)
		setDatabaseIndex(self.indexDB)

		# Persist all pending configuration changes.
		from config import conf

		conf.save()

	def getCurrentDatabasePath(self) -> str:
		"""
		Return the path of the currently selected database.

		If the selected database path is empty, use the primary
		database path as a fallback.

		Raises:
			ValueError: If no valid database path is available.
		"""
		path = self.firstDatabase if self.indexDB == 0 else self.altDatabase

		if path and path.strip():
			return path

		if self.firstDatabase and self.firstDatabase.strip():
			return self.firstDatabase

		raise ValueError("No valid database path defined.")

	def reload(self):
		"""
		Reload database settings from the add-on configuration.
		"""
		self.loadConfig()

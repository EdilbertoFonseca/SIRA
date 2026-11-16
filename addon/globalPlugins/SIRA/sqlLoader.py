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

Created on: 19/02/2026
"""

import os
import sys
from typing import Any

from logHandler import log

from .varsConfig import ADDON_PATH

LIB_FOLDER = "lib64"
LIB_PATH = os.path.join(ADDON_PATH, LIB_FOLDER)

# Add the library path to sys.path when available.
if os.path.isdir(LIB_PATH) and LIB_PATH not in sys.path:
	sys.path.insert(0, LIB_PATH)

# Initialize the SQL module.
sql: Any = None

try:
	import sqlite3 as sql
except ImportError as error:
	log.error(
		f"Failed to load the SQLite module: {error}",
		exc_info=True,
	)
	raise

if sql is None:
	raise ImportError("SQLite module could not be initialized.")


def initializeDatabase(dbPath: str):
	"""
	Initialize the database and create the required tables.

	Args:
		dbPath: Full path to the database file.
	"""

	dbDir = os.path.dirname(dbPath)

	# Create the database directory when necessary.
	if dbDir:
		os.makedirs(dbDir, exist_ok=True)

	connection = None

	try:
		connection = sql.connect(dbPath)

		connection.execute(
			"""
			CREATE TABLE IF NOT EXISTS contacts(
				id INTEGER PRIMARY KEY,
				secretaryOffice TEXT,
				landline TEXT,
				sector TEXT,
				responsible TEXT,
				extension TEXT,
				cell TEXT,
				email TEXT
			)
			""",
		)

		connection.commit()

	except sql.Error:
		if connection:
			connection.rollback()
		raise

	finally:
		if connection:
			connection.close()

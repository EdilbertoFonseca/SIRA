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

import globalVars

from .dbConfig import DatabaseConfig
from .sqlLoader import sql, initializeDatabase


# Define the default database location.
CONFIG_PATH = str(getattr(globalVars.appArgs, "configPath", ""))
ADDON_DATA_DIR = os.path.join(CONFIG_PATH, "SIRA")
DEFAULT_DB_PATH = os.path.join(ADDON_DATA_DIR, "database.db")

# Initialize the database configuration.
DB = DatabaseConfig(DEFAULT_DB_PATH)
DB.loadConfig()


class ObjectExtensionRegistrationSystem(object):
	def __init__(
		self,
		id="",
		secretaryOffice="",
		landline="",
		sector="",
		responsible="",
		extension="",
		cell="",
		email="",
	):
		"""
		Initialize a new contact with the provided details.

		Args:
			id (str): Unique contact identifier.
			secretaryOffice (str): Name of the secretariat.
			landline (str): Secretariat contact.
			sector (str): Sector linked to the secretariat.
			responsible (str): Name of the person responsible for the sector.
			extension (str): Sector extension.
			cell (str): Contact's cell phone number.
			email (str): Contact email address.
		"""
		super().__init__()
		self.id = id
		self.secretaryOffice = secretaryOffice
		self.landline = landline
		self.sector = sector
		self.responsible = responsible
		self.extension = extension
		self.cell = cell
		self.email = email

	def __repr__(self):
		"""
		Return a formatted representation of the contact.

		Returns:
			str: A formatted string containing the contact information.
		"""
		return (
			f"SecretaryOffice: {self.secretaryOffice}, "
			f"Landline: {self.landline}, "
			f"Sector: {self.sector}, "
			f"Responsible: {self.responsible}, "
			f"Extension: {self.extension}, "
			f"Cell: {self.cell}, "
			f"Email: {self.email}"
		)


class Section(object):
	def __init__(self):
		"""Initialize the database connection state."""
		super().__init__()
		self.connect = None
		self.cursor = None
		self.connected = False

	def __enter__(self):
		"""Open a database connection and prepare the cursor."""

		# Reload the configuration to use the latest settings.
		DB.reload()

		dbPath = DB.getCurrentDatabasePath()

		# Ensure that the database and its required tables exist.
		initializeDatabase(dbPath)

		# Establish the database connection.
		self.connect = sql.connect(dbPath)
		self.connect.row_factory = self.dictFactory
		self.cursor = self.connect.cursor()
		self.connected = True

		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		"""Close the database connection."""

		try:
			if self.connect:
				self.connect.close()
		finally:
			self.connect = None
			self.cursor = None
			self.connected = False

		return False

	def execute(self, sql, parms=None):
		"""Execute an SQL query."""

		if not self.connected:
			return False

		if parms is None:
			self.cursor.execute(sql)
		else:
			self.cursor.execute(sql, parms)

		return True

	def executemany(self, sql, parms=None):
		"""Execute an SQL query with multiple parameter sets."""

		if not self.connected:
			return False

		if parms is None:
			self.cursor.executemany(sql)
		else:
			self.cursor.executemany(sql, parms)

		return True

	def dictFactory(self, cursor, row):
		"""Convert a database row into a dictionary."""

		return {column[0]: row[index] for index, column in enumerate(cursor.description)}

	def fetchall(self):
		"""Retrieve all rows from the executed query."""

		return self.cursor.fetchall()

	def persist(self):
		"""Commit the current database transaction."""

		if not self.connected:
			return False

		self.connect.commit()
		return True

	@classmethod
	def initDB(cls):
		"""Initialize the database and create its required tables."""

		DB.reload()
		initializeDatabase(DB.getCurrentDatabasePath())

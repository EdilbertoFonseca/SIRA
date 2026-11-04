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
from .sqlLoader import sql

# 1. First we define where the data lives
# We force conversion to string to avoid Optional[str]
CONFIG_PATH = str(getattr(globalVars.appArgs, "configPath", ""))
ADDON_DATA_DIR = os.path.join(CONFIG_PATH, "SIRA")

if not os.path.isdir(ADDON_DATA_DIR):
	os.makedirs(ADDON_DATA_DIR)

# 2. We set the default path
DEFAULT_DB_PATH = os.path.join(
	ADDON_DATA_DIR,
	"database.db",
)

# If line 106 is something like os.path.dirname(DEFAULT_DB_PATH)
# Make sure the argument is unambiguous:
BASE_DIR = os.path.dirname(str(DEFAULT_DB_PATH))

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
		Initializes a new contact with the provided details.

		Args:
			id (str): Unique contact identifier.
			secretaryOffice (str): Name of the secretariat.
			landline (str): Secretariat contact.
			sector (str): Sector linked to the secretariat.
			responsible(str): Name of person responsible for the sector.
			extension (str): Sector extension.
			cell (str): Contact's cell phone number.
			email (str): Contact email address.
		"""
		super().__init__()  # calls the init of the parent class (silences linters and maintains compatibility)
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
		Returns a formatted string that represents the NVDA Extension Registration System contact.

		Returns:
			str: A formatted string with the contact's secretary, sector, landline, responsible, extension, cell, and email.
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


class Section:
	connect = None
	cursor = None
	connected = False

	def __enter__(self):
		"""Input method for the context manager."""
		DB_PATH = DB.getCurrentDatabasePath()

		# Ensure that the file folder exists.
		DB_DIR = os.path.dirname(DB_PATH)
		if DB_DIR and not os.path.exists(DB_DIR):
			os.makedirs(DB_DIR)

		self.connect = sql.connect(DB_PATH)
		self.connect.row_factory = self.dictFactory
		self.cursor = self.connect.cursor()
		self.connected = True
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		"""Exit method for the context manager."""
		if self.connect:
			self.connect.close()
		self.connected = False
		return False

	# The `connect` and `disconnect` methods have been removed.

	def execute(self, sql, parms=None):
		"""Executes an SQL query on the database."""
		if self.connected:
			if parms is None:
				self.cursor.execute(sql)
			else:
				self.cursor.execute(sql, parms)
			return True
		return False

	def executemany(self, sql, parms=None):
		"""Executes multiple SQL queries on the database."""
		if self.connected:
			if parms is None:
				self.cursor.executemany(sql)
			else:
				self.cursor.executemany(sql, parms)
			return True
		return False

	def dictFactory(self, cursor, row):
		"""Converts the result of a query into a dictionary."""
		return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

	def fetchall(self):
		"""Retrieves all rows from the result of a query."""
		# A linha self.connect.row_factory = self.dict_factory foi movida para o __enter__
		return self.cursor.fetchall()

	def persist(self):
		"""Confirms the changes made in a database transaction."""
		if self.connected:
			self.connect.commit()
			return True
		return False

	@classmethod
	def initDB(cls):
		"""Checks the existence of the database and creates the contact table if it does not exist."""
		with cls() as trans:
			sqlCommand = """CREATE TABLE IF NOT EXISTS contacts(
				id INTEGER PRIMARY KEY,
				secretaryOffice TEXT,
				landline TEXT,
				sector TEXT,
				responsible TEXT,
				extension TEXT,
				cell TEXT,
				email TEXT)"""
			trans.execute(sqlCommand)
			trans.persist()

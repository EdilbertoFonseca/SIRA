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

import globalVars

from .dbConfig import DatabaseConfig
from .sqlLoader import sql

ADDON_DATA_DIR = os.path.join(globalVars.appArgs.configPath, "SIRA")  # pyright: ignore[reportCallIssue]

if not os.path.isdir(ADDON_DATA_DIR):
	os.makedirs(ADDON_DATA_DIR)

DEFAULT_DB_PATH = os.path.join(
	ADDON_DATA_DIR,
	"database.db",
)

db = DatabaseConfig(DEFAULT_DB_PATH)
db.load_config()


class ObjectExtensionRegistrationSystem(object):
	def __init__(
		self,
		id="",
		secretary_office="",
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
			secretary_office (str): Name of the secretariat.
			landline (str): Secretariat contact.
			sector (str): Sector linked to the secretariat.
			responsible(str): Name of person responsible for the sector.
			extension (str): Sector extension.
			cell (str): Contact's cell phone number.
			email (str): Contact email address.
		"""
		super().__init__()  # calls the init of the parent class (silences linters and maintains compatibility)
		self.id = id
		self.secretary_office = secretary_office
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
			f"SecretaryOffice: {self.secretary_office}, "
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
		"""Método de entrada para o gerenciador de contexto."""
		self.connect = sql.connect(db.get_current_database_path())
		self.connect.row_factory = self.dict_factory  # Adicionado aqui para consistência
		self.cursor = self.connect.cursor()
		self.connected = True
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		"""Método de saída para o gerenciador de contexto."""
		if self.connect:
			self.connect.close()
		self.connected = False
		return False

	# Métodos connection e disconnect foram removidos.

	def execute(self, sql, parms=None):
		"""Executa uma consulta SQL no banco de dados."""
		if self.connected:
			if parms is None:
				self.cursor.execute(sql)
			else:
				self.cursor.execute(sql, parms)
			return True
		return False

	def executemany(self, sql, parms=None):
		"""Executa várias consultas SQL no banco de dados."""
		if self.connected:
			if parms is None:
				self.cursor.executemany(sql)
			else:
				self.cursor.executemany(sql, parms)
			return True
		return False

	def dict_factory(self, cursor, row):
		"""Converte o resultado de uma consulta em um dicionário."""
		return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

	def fetchall(self):
		"""Recupera todas as linhas do resultado de uma consulta."""
		# A linha self.connect.row_factory = self.dict_factory foi movida para o __enter__
		return self.cursor.fetchall()

	def persist(self):
		"""Confirma as alterações feitas em uma transação de banco de dados."""
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
				secretary_office TEXT,
				landline TEXT,
				sector TEXT,
				responsible TEXT,
				extension TEXT,
				cell TEXT,
				email TEXT)"""
			trans.execute(sqlCommand)
			trans.persist()

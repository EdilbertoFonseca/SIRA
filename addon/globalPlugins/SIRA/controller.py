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
import sys

import addonHandler
from logHandler import log

from .model import ObjectExtensionRegistrationSystem, Section
from .sqlLoader import sql
from .varsConfig import ADDON_PATH, is64

# Add the lib/ folder to sys.path (only once)
libFolder = "lib64" if is64 else "lib"
libPath = os.path.join(ADDON_PATH, libFolder)

if os.path.isdir(libPath) and libPath not in sys.path:
	sys.path.insert(0, libPath)

try:
	import csv
except ImportError as e:
	log.error("Error importing the module: {}".format(str(e)))
	raise ImportError("The required library is absent: csv.")

# Initialize translation support
addonHandler.initTranslation()


def get_all_records():
	"""
	Function that retrieves all data from the database.

	This function queries the database to obtain all stored records
	in the contact table, sorted alphabetically by name. The results are converted
	into `ObjectContact` objects and returned as a list.

	Returns:
					list: A list of `ObjectContact` objects representing all records in the database.
	"""
	with Section() as trans:
		trans.execute("SELECT * FROM contacts ORDER BY secretary_office ASC")
		results = trans.fetchall()
	return convert_results(results)


def convert_results(results):
	"""
	Converts the results to objects `objectcontact`.

	This function receives a list of database consultation results, where each result is a dictionary,
	and convert these results into objects 'objectcontact'.

	Args:
					results (list): A list of dictionaries, where each dictionary represents a contact record.

	Returns:
					List: A list of objects `Objectcontact`, where each object represents a contact in the database.
	"""

	rows = [
		ObjectExtensionRegistrationSystem(
			record["id"],
			record["secretary_office"],
			record["landline"],
			record["sector"],
			record["responsible"],
			record["extension"],
			record["cell"],
			record["email"],
		)
		for record in results
	]
	return rows


def add_record(data):
	"""
	Insert new records into the database.
	"""
	required_keys = [
		"secretary_office",
		"landline",
		"sector",
		"responsible",
		"extension",
		"cell",
		"email",
	]
	contact_data = data.get("contacts")  # Acesse a chave 'contacts'

	if not contact_data:
		raise ValueError(_("Missing 'contacts' key in dictionary"))

	for key in required_keys:
		if key not in contact_data:
			raise ValueError(_(f"Missing key in dictionary: {key}"))

	try:
		with Section() as trans:
			trans.execute(
				"""INSERT INTO contacts (secretary_office, landline, sector, responsible, extension, cell, email)
				VALUES (?, ?, ?, ?, ?, ?, ?)""",
				(
					contact_data["secretary_office"],
					contact_data["landline"],
					contact_data["sector"],
					contact_data["responsible"],
					contact_data["extension"],
					contact_data["cell"],
					contact_data["email"],
				),
			)
			trans.persist()
	except Exception as e:
		log.error(_("Error inserting record: {}").format(e))
		raise


def search_records(filterChoice, keyword):
	"""
	Search registrations in the database based on the chosen filter and the keyword provided by the user.

		ARGS:
						Filterchoice (STR): The filter criterion to be used in the research.
										Possible options are:
														- 'Secretary Office' (Secretariat): filters records by the name of the secretary.
														- 'Landline' (landline): filters records by the landline number of the contact.
														- 'sector' (sector): filters records by the contact sector.
														- 'Responsible' (responsible): filters records by the responsible person.
														- 'Extension' (extension): filters records by the extension number.
														- 'Cell Phone' (mobile): filters records by the mobile number of the contact.
														- 'Email' (email): filters records by the contact email address.

						Keyword (STR): The keyword to be used in the search. It can be a part of the name, phone number or email, depending on the chosen filter.

		Returns:
						List: A list of objects `Objectcontact` corresponding to the records found.
	"""

	query_map = {
		_("Secretary office"): "SELECT * FROM contacts WHERE secretary_office LIKE ?",
		_("Landline"): "SELECT * FROM contacts WHERE landline LIKE ?",
		_("Sector"): "SELECT * FROM contacts WHERE sector LIKE ?",
		_("Responsible"): "SELECT * FROM contacts WHERE responsible LIKE ?",
		_("Extension"): "SELECT * FROM contacts WHERE extension LIKE ?",
		_("Cell phone"): "SELECT * FROM contacts WHERE cell LIKE ?",
		_("Email"): "SELECT * FROM contacts WHERE email LIKE ?",
	}

	# Check if the chosen filter is valid
	query = query_map.get(filterChoice, "")
	if filterChoice not in query_map.keys():
		raise ValueError(f"Invalid filter choice: {filterChoice}")

	with Section() as trans:
		trans.execute(query, ("%" + keyword + "%",))
		results = trans.fetchall()

	return convert_results(results)


def edit_record(ID, row):
	"""
	Function to update records in the database.

	Args:
					ID (int): The unique identifier of the record that will be updated.
					row (dict): A dictionary containing the new values for the registration.
									The expected keys in the dictionary are:
													- 'secretary_office' (str): The new name of the contact secretariat.
													- 'landline' (str): The new contact phone number of the contact.
													- 'sector' (str): The new sector or department.
													- 'responsible' (str): The new responsible for contact.
													- 'extension' (str): The new contact branch number.
													- 'cell' (str): The new phone number of contact.
													- 'email' (str): The new contact email address.
	"""

	with Section() as trans:
		trans.execute(
			"UPDATE contacts SET secretary_office = ?, landline = ?, sector = ?, responsible = ?, extension = ?, cell = ?, email = ? WHERE id = ?",
			(
				row["secretary_office"],
				row["landline"],
				row["sector"],
				row["responsible"],
				row["extension"],
				row["cell"],
				row["email"],
				ID,
			),
		)
		trans.persist()


def delete(id):
	"""
	Função para remover um registro do banco de dados com tratamento de erro.

	Args:
		id (int): O identificador único do registro a ser removido.
	"""
	try:
		with Section() as trans:
			if not trans.connected:
				log.warning("Não foi possível conectar ao banco de dados para deletar o registro.")
				return False

			trans.execute("DELETE FROM contacts WHERE id=?", (id,))
			trans.persist()
			log.info(f"Registro com ID {id} deletado com sucesso.")
			return True

	except sql.Error as e:
		log.error(f"Erro ao deletar registro (ID: {id}): {e.__class__.__name__} - {e}")
		return False


def reset_record():
	"""
	Delete all records from the database.
	"""
	with Section() as trans:
		trans.execute("DELETE FROM contacts")
		trans.persist()


def import_csv_to_db(mypath):
	"""
	Import data from a CSV file to the database.

	Args:
					mypath (str): O caminho para o arquivo CSV que contém os dados a serem importados.

	Raises:
					FileNotFoundError: Se o arquivo CSV especificado não existir.
					csv.Error: Se ocorrer um erro ao processar o arquivo CSV.
	"""

	if not isinstance(mypath, str) or not os.path.isfile(mypath):
		raise FileNotFoundError(
			f"The file at {mypath} does not exist or is not a valid path.",
		)

	with Section() as trans:
		try:
			with open(mypath, "r", encoding="UTF-8") as file:
				# Detects the delimiter automatically
				first_line = file.readline()
				detected_delimiter = csv.Sniffer().sniff(first_line).delimiter
				file.seek(0)  # Retorna ao início do arquivo

				contents = csv.reader(file, delimiter=detected_delimiter)

				insert_records = """
				INSERT INTO contacts (secretary_office, landline, sector, responsible, extension, cell, email)
				SELECT ?, ?, ?, ?, ?, ?, ?
				WHERE NOT EXISTS (
					SELECT 1 FROM contacts
					WHERE secretary_office = ?
					AND landline = ?
					AND sector = ?
					AND responsible = ?
					AND extension = ?
					AND cell = ?
					AND email = ?
				)"""
				data_to_insert = []
				for row in contents:
					if len(row) == 7:
						secretary_office, landline, sector, responsible, extension, cell, email = row
						# Duplicates the values ​​to meet SQL
						data_to_insert.append(
							(
								secretary_office,
								landline,
								sector,
								responsible,
								extension,
								cell,
								email,  # Para o INSERT
								secretary_office,
								landline,
								sector,
								responsible,
								extension,
								cell,
								email,  # Para o WHERE
							),
						)
					else:
						log.warning(
							f"Skipping row {contents.line_num} with incorrect number of columns: {row}",
						)

			if data_to_insert:
				trans.executemany(insert_records, data_to_insert)
			trans.persist()

		except (FileNotFoundError, csv.Error, UnicodeDecodeError) as e:
			log.error(f"Error importing data: {str(e)}")
			raise


def export_db_to_csv(mypath):
	try:
		with Section() as trans:
			trans.execute("SELECT * FROM contacts")
			rows = trans.fetchall()  # Isso retorna uma lista de dicionários.

			# Use os nomes das colunas para extrair os valores, excluindo o 'id'.
			# Isso é seguro porque os dicionários são hashable e têm chaves.
			cleaned_rows = [
				[
					row["secretary_office"],
					row["landline"],
					row["sector"],
					row["responsible"],
					row["extension"],
					row["cell"],
					row["email"],
				]
				for row in rows
			]

			with open(mypath, "w", newline="", encoding="utf-8") as file:
				writer = csv.writer(file)
				writer.writerows(cleaned_rows)
	except Exception as e:
		log.error(f"Erro ao exportar dados para CSV: {str(e)}")
		# A exceção deve ser relançada para notificar a interface
		raise


def count_records():
	"""
	It counts the total number of records in the database safely.

	Returns:
		INT: The total number of records.
		None: In case of error when accessing the database.
	"""
	try:
		with Section() as trans:
			if not trans.connected:
				return None

			trans.execute("SELECT COUNT(*) FROM contacts")
			# Access the value of the dictionary by the 'Count (*)' key instead of the index [0].
			count = trans.cursor.fetchone()["COUNT(*)"]
			return count
	except Exception as e:
		log.error(f"Erro ao contar registros no banco de dados: {e.__class__.__name__} - {e}")
		return None


def save_csv(filtered_item, mypath):
	"""
		Save the filtered items in a CSV file on the specified path.

	This function receives a list of filtered items and exports its information
		for a CSV file. CSV columns are mapped to the attributes of
		items according to the predefined dictionary. If the file already exists, it will be
		envelope. The CSV file is generated in "Latin-1" format with point and comma delimiter.

		Args:
			filtered_item (list): List of objects whose data will be exported to the CSV file.
			mypath (str): Way where the CSV file will be saved.

		Exceptions:
	No exception is explicitly managed within this function, but if there is
			problems when writing in the file (such as permissions or I/O errors), an exception
			Standard will be launched by Python.
	"""

	# Check if Filtered Item is a list
	if isinstance(filtered_item, list):
		# Mapping between CSV columns and object attributes
		column_to_attribute = {
			"Secretaria": "secretary_office",
			"Telefone fixo": "landline",
			"Setor": "sector",
			"Responsável": "responsible",
			"Ramal": "extension",
			"Telefone celular": "cell",
			"E-mail": "email",
		}

		# Open the file once and write all data
		with open(mypath, mode="w", newline="", encoding="Latin-1") as file:
			writer = csv.writer(file, delimiter=";")

			# Writing the header
			# Set the columns directly
			colunas = list(column_to_attribute.keys())  # Obtém as chaves do mapeamento
			writer.writerow(colunas)

			# Write the data (items data)
			for item in filtered_item:
				dados_item = []
				for col in column_to_attribute.values():  # Iterar sobre os atributos mapeados
					# Checking if the attribute exists in the item
					valor = getattr(item, col, "")  # Pega o valor do atributo ou um valor vazio
					dados_item.append(valor)

				# Write item data in the CSV file
				writer.writerow(dados_item)


def find_duplicate_records():
	"""
	Busca registros duplicados na tabela de contatos.
	"""
	try:
		with Section() as trans:
			if not trans.connected:
				log.warning("Não foi possível conectar ao banco de dados para buscar duplicatas.")
				return []

			# AQUI ESTÁ A CORREÇÃO: "AS ids" dá um apelido à coluna para facilitar o acesso.
			sql_find_duplicates = """
			SELECT
				group_concat(id) AS ids, secretary_office, landline, sector, responsible, extension, cell, email
			FROM contacts
			GROUP BY secretary_office, landline, sector, extension
			HAVING count(*) > 1
			"""
			trans.execute(sql_find_duplicates)

			duplicate_groups = trans.cursor.fetchall()

			if not duplicate_groups:
				return []

			all_duplicate_ids = []
			for group in duplicate_groups:
				# ACESSA O VALOR USANDO O APELIDO 'ids'
				ids_str = group["ids"]
				ids = ids_str.split(",")
				all_duplicate_ids.extend(ids)

			placeholders = ",".join(["?"] * len(all_duplicate_ids))
			sql_fetch_duplicates = f"SELECT * FROM contacts WHERE id IN ({placeholders})"
			trans.execute(sql_fetch_duplicates, all_duplicate_ids)

			duplicate_records = [
				ObjectExtensionRegistrationSystem(**record) for record in trans.cursor.fetchall()
			]

			return duplicate_records

	except Exception as e:
		log.error(f"Erro ao buscar registros duplicados: {e.__class__.__name__} - {e}")
		return []

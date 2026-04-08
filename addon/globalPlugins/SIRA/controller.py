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
from .varsConfig import ADDON_PATH, IS64

# Add the lib/ folder to sys.path (only once)
libFolder = "lib64" if IS64 else "lib"
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


def getAllRecords():
	"""
	Function that retrieves all data from the database.

	This function queries the database to obtain all stored records
	in the contact table, sorted alphabetically by name. The results are converted
	into `ObjectContact` objects and returned as a list.

	Returns:
					list: A list of `ObjectContact` objects representing all records in the database.
	"""
	with Section() as trans:
		trans.execute("SELECT * FROM contacts ORDER BY secretaryOffice ASC")
		results = trans.fetchall()
	return convertResults(results)


def convertResults(results):
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
			record["secretaryOffice"],
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


def addRecord(data):
	"""
	Insert new records into the database.
	"""
	requiredKeys = [
		"secretaryOffice",
		"landline",
		"sector",
		"responsible",
		"extension",
		"cell",
		"email",
	]
	contactData = data.get("contacts")  # Acesse a chave 'contacts'

	if not contactData:
		raise ValueError(_("Missing 'contacts' key in dictionary"))

	for key in requiredKeys:
		if key not in contactData:
			raise ValueError(_(f"Missing key in dictionary: {key}"))

	try:
		with Section() as trans:
			trans.execute(
				"""INSERT INTO contacts (secretaryOffice, landline, sector, responsible, extension, cell, email)
				VALUES (?, ?, ?, ?, ?, ?, ?)""",
				(
					contactData["secretaryOffice"],
					contactData["landline"],
					contactData["sector"],
					contactData["responsible"],
					contactData["extension"],
					contactData["cell"],
					contactData["email"],
				),
			)
			trans.persist()
	except Exception as e:
		log.error(_("Error inserting record: {}").format(e))
		raise


def searchRecords(filterChoice, keyword):
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

	queryMap = {
		_("Secretary office"): "SELECT * FROM contacts WHERE secretaryOffice LIKE ?",
		_("Landline"): "SELECT * FROM contacts WHERE landline LIKE ?",
		_("Sector"): "SELECT * FROM contacts WHERE sector LIKE ?",
		_("Responsible"): "SELECT * FROM contacts WHERE responsible LIKE ?",
		_("Extension"): "SELECT * FROM contacts WHERE extension LIKE ?",
		_("Cell phone"): "SELECT * FROM contacts WHERE cell LIKE ?",
		_("Email"): "SELECT * FROM contacts WHERE email LIKE ?",
	}

	# Check if the chosen filter is valid
	query = queryMap.get(filterChoice, "")
	if filterChoice not in queryMap.keys():
		raise ValueError(f"Invalid filter choice: {filterChoice}")

	with Section() as trans:
		trans.execute(query, ("%" + keyword + "%",))
		results = trans.fetchall()

	return convertResults(results)


def editRecord(ID, row):
	"""
	Function to update records in the database.

	Args:
					ID (int): The unique identifier of the record that will be updated.
					row (dict): A dictionary containing the new values for the registration.
									The expected keys in the dictionary are:
													- 'secretaryOffice' (str): The new name of the contact secretariat.
													- 'landline' (str): The new contact phone number of the contact.
													- 'sector' (str): The new sector or department.
													- 'responsible' (str): The new responsible for contact.
													- 'extension' (str): The new contact branch number.
													- 'cell' (str): The new phone number of contact.
													- 'email' (str): The new contact email address.
	"""

	with Section() as trans:
		trans.execute(
			"UPDATE contacts SET secretaryOffice = ?, landline = ?, sector = ?, responsible = ?, extension = ?, cell = ?, email = ? WHERE id = ?",
			(
				row["secretaryOffice"],
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
	Function to remove a record from the database with error handling.

	Args:
		id (int): The unique identifier of the record to be removed.
	"""
	try:
		with Section() as trans:
			if not trans.connected:
				log.warning("Unable to connect to database to delete record.")
				return False

			trans.execute("DELETE FROM contacts WHERE id=?", (id,))
			trans.persist()
			log.info(f"Registro com ID {id} deletado com sucesso.")
			return True

	except sql.Error as e:
		log.error(f"Error deleting record (ID: {id}): {e.__class__.__name__} - {e}")
		return False


def resetRecord():
	"""
	Delete all records from the database.
	"""
	with Section() as trans:
		trans.execute("DELETE FROM contacts")
		trans.persist()


def importCsvToDb(myPath):
	"""
	Import data from a CSV file to the database.

	Args:
					mypath (str): The path to the CSV file that contains the data to be imported.

	Raises:
					FileNotFoundError: If the specified CSV file does not exist.
					csv.Error: If an error occurs while processing the CSV file.
	"""

	if not isinstance(myPath, str) or not os.path.isfile(myPath):
		raise FileNotFoundError(
			f"The file at {myPath} does not exist or is not a valid path.",
		)

	with Section() as trans:
		try:
			with open(myPath, "r", encoding="UTF-8") as file:
				# Detects the delimiter automatically
				firstLine = file.readline()
				detectedDelimiter = csv.Sniffer().sniff(firstLine).delimiter
				file.seek(0)  # Returns to the beginning of the file

				contents = csv.reader(file, delimiter=detectedDelimiter)

				insertRecords = """
				INSERT INTO contacts (secretaryOffice, landline, sector, responsible, extension, cell, email)
				SELECT ?, ?, ?, ?, ?, ?, ?
				WHERE NOT EXISTS (
					SELECT 1 FROM contacts
					WHERE secretaryOffice = ?
					AND landline = ?
					AND sector = ?
					AND responsible = ?
					AND extension = ?
					AND cell = ?
					AND email = ?
				)"""
				dataToInsert = []
				for row in contents:
					if len(row) == 7:
						secretaryOffice, landline, sector, responsible, extension, cell, email = row
						# Duplicates the values ​​to meet SQL
						dataToInsert.append(
							(
								secretaryOffice,
								landline,
								sector,
								responsible,
								extension,
								cell,
								email,  # Para o INSERT
								secretaryOffice,
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

			if dataToInsert:
				trans.executemany(insertRecords, dataToInsert)
			trans.persist()

		except (FileNotFoundError, csv.Error, UnicodeDecodeError) as e:
			log.error(f"Error importing data: {str(e)}")
			raise


def exportDBToCsv(myPath):
	try:
		with Section() as trans:
			trans.execute("SELECT * FROM contacts")
			rows = trans.fetchall()  # This returns a list of dictionaries.

			# Use the column names to extract the values, excluding the 'id'.
			# This is secure because dictionaries are hashable and have keys.
			cleanedRows = [
				[
					row["secretaryOffice"],
					row["landline"],
					row["sector"],
					row["responsible"],
					row["extension"],
					row["cell"],
					row["email"],
				]
				for row in rows
			]

			with open(myPath, "w", newline="", encoding="utf-8") as file:
				writer = csv.writer(file)
				writer.writerows(cleanedRows)
	except Exception as e:
		log.error(f"Error exporting data to CSV: {str(e)}")
		# The exception must be rethrown to notify the interface
		raise


def countRecords():
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
		log.error(f"Error counting records in database: {e.__class__.__name__} - {e}")
		return None


def saveCsv(filteredItem, myPath):
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
	if isinstance(filteredItem, list):
		# Mapping between CSV columns and object attributes
		columnToAttribute = {
			"Secretaria": "secretaryOffice",
			"Landline": "landline",
			"Sector": "sector",
			"Responsible": "responsible",
			"Extension": "extension",
			"Cell phone": "cell",
			"E-mail": "email",
		}

		# Open the file once and write all data
		with open(myPath, mode="w", newline="", encoding="Latin-1") as file:
			writer = csv.writer(file, delimiter=";")

			# Writing the header
			# Set the columns directly
			colunas = list(columnToAttribute.keys())  # Gets the mapping keys
			writer.writerow(colunas)

			# Write the data (items data)
			for item in filteredItem:
				dadosItem = []
				for col in columnToAttribute.values():  # Iterate over mapped attributes
					# Checking if the attribute exists in the item
					valor = getattr(item, col, "")  # Gets the attribute value or an empty value
					dadosItem.append(valor)

				# Write item data in the CSV file
				writer.writerow(dadosItem)


def findDuplicateRecords():
	"""
	Searches for duplicate records in the contact table.
	"""
	try:
		with Section() as trans:
			if not trans.connected:
				log.warning("Unable to connect to database to search for duplicates.")
				return []

			# Find duplicates
			sql_find_duplicates = """
			SELECT
				group_concat(id) AS ids, secretaryOffice, landline, sector, responsible, extension, cell, email
			FROM contacts
			GROUP BY secretaryOffice, landline, sector, extension
			HAVING count(*) > 1
			"""
			trans.execute(sql_find_duplicates)

			duplicateGroups = trans.cursor.fetchall()

			if not duplicateGroups:
				return []

			allDuplicateIds = []
			for group in duplicateGroups:
				# Access the value using the alias 'ids'
				idsStr = group["ids"]
				ids = idsStr.split(",")
				allDuplicateIds.extend(ids)

			placeholders = ",".join(["?"] * len(allDuplicateIds))
			sqlFetchDuplicates = f"SELECT * FROM contacts WHERE id IN ({placeholders})"
			trans.execute(sqlFetchDuplicates, allDuplicateIds)

			duplicateRecords = [
				ObjectExtensionRegistrationSystem(**record) for record in trans.cursor.fetchall()
			]

			return duplicateRecords

	except Exception as e:
		log.error(f"Error when searching for duplicate records: {e.__class__.__name__} - {e}")
		return []

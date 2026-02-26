# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

Created on: 22/08/2025
"""

import wx
import addonHandler
import gui
from . import controller as core

# Initialize translation support
addonHandler.initTranslation()


class ManageDuplicatesDialog(wx.Dialog):
	def __init__(self, parent, duplicates):
		super(ManageDuplicatesDialog, self).__init__(
			parent,
			title=_("Manage Duplicate Records"),
			size=(700, 500),
		)
		self.duplicates = duplicates
		self.parent = parent
		# Dictionary to map the list index to the record ID
		self.list_map = {}

		self.panel = wx.Panel(self)
		mainSizer = wx.BoxSizer(wx.VERTICAL)

		description = wx.StaticText(
			self.panel,
			label=_("Found the following duplicate records. Select the ones you want to remove."),
		)
		mainSizer.Add(description, 0, wx.ALL | wx.EXPAND, 10)

		# Creation of the list to display records
		# WX.LC Report style allows columns.
		# We do not use Wx.lc Single Sel to allow multiple selections.
		self.duplicateList = wx.ListCtrl(
			self.panel,
			style=wx.LC_REPORT,
		)
		mainSizer.Add(self.duplicateList, 1, wx.ALL | wx.EXPAND, 10)

		self.initialize_duplicate_list()

		# Action buttons
		buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

		# Button to remove selected items
		self.removeSelectedButton = wx.Button(self.panel, label=_("Remove Selected"))
		self.removeSelectedButton.Bind(wx.EVT_BUTTON, self.onRemoveSelected)
		buttonSizer.Add(self.removeSelectedButton, 0, wx.ALL, 5)

		# Close button
		self.closeButton = wx.Button(self.panel, label=_("Close"))
		self.closeButton.Bind(wx.EVT_BUTTON, self.onClose)
		buttonSizer.Add(self.closeButton, 0, wx.ALL, 5)

		mainSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)

		self.panel.SetSizer(mainSizer)
		mainSizer.Fit(self)

	def initialize_duplicate_list(self):
		"""Fill in the list of duplicates with the data."""
		self.duplicateList.ClearAll()
		self.list_map.clear()

		columns = [
			(_("ID"), 50),
			(_("Secretary Office"), 120),
			(_("Landline"), 100),
			(_("Extension"), 80),
			(_("Sector"), 120),
			(_("Responsible"), 120),
			(_("Email"), 200),
		]

		for i, (title, width) in enumerate(columns):
			self.duplicateList.InsertColumn(i, title, width=width)

		for i, record in enumerate(self.duplicates):
			index = self.duplicateList.InsertItem(self.duplicateList.GetItemCount(), str(record.id))
			self.duplicateList.SetItem(index, 1, record.secretary_office)
			self.duplicateList.SetItem(index, 2, record.landline)
			self.duplicateList.SetItem(index, 3, record.extension)
			self.duplicateList.SetItem(index, 4, record.sector)
			self.duplicateList.SetItem(index, 5, record.responsible)
			self.duplicateList.SetItem(index, 6, record.email)
			self.list_map[index] = record.id

	def onRemoveSelected(self, event):
		"""Dress with the removal of the selected records."""
		selected_indices = []
		item = -1
		while True:
			# Get the next selected item
			item = self.duplicateList.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
			if item == -1:
				break
			selected_indices.append(item)

		if not selected_indices:
			gui.messageBox(_("No records selected for removal."), _("Attention"))
			return

		message = _("Are you sure you want to remove the selected duplicate records?")
		caption = _("Confirm Deletion")
		user_response = gui.messageBox(message, caption, style=wx.YES_NO | wx.ICON_QUESTION)

		if user_response == wx.YES:
			deleted_count = 0
			for index in selected_indices:
				record_id = self.list_map.get(index)
				if record_id:
					if core.delete(record_id):
						deleted_count += 1

			gui.messageBox(
				_("%d selected records were removed.") % deleted_count,
				_("Removal Complete"),
			)

			# Update the list after removal
			remaining_duplicates = core.find_duplicate_records()
			if remaining_duplicates:
				self.duplicates = remaining_duplicates
				self.initialize_duplicate_list()
			else:
				self.Destroy()
				self.parent._refresh_and_focus()

	def onClose(self, event):
		"""Closes the dialogue."""
		self.Destroy()

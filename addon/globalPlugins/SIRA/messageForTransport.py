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

Created on: 07/02/2025
"""

import os
import re
import sys
from datetime import datetime

import addonHandler
import gui
import wx
from logHandler import log

from .varsConfig import ADDON_NAME, ADDON_PATH, IS64, MASK_DATE, MASK_PHONE, MASK_TIME

# Add the lib/ folder to sys.path (only once)
libFolder = "lib64" if IS64 else "lib"
libPath = os.path.join(ADDON_PATH, libFolder)

if os.path.isdir(libPath) and libPath not in sys.path:
	sys.path.insert(0, libPath)

try:
	from maskedTextCtrl import MaskedTextCtrl
except ImportError as e:
	log.error(f"[{ADDON_NAME}] Error when importing internal library 'MaskedTextCtrl': {e}")
	raise ImportError(_("Mandatory Library Absent: MaskedTextCtrl"))


# Initializes the translation
addonHandler.initTranslation()


class MessageForTransport(wx.Dialog):
	"""
	Diálogo para o envio e armazenamento de mensagens de recado.

	Esta classe representa uma janela de diálogo no wxPython para coletar informações do remetente,
	incluindo nome, assunto, mensagem, data e hora da viagem, ponto de encontro e telefone.

	Atributos:
			_instance (AddonDialog): Instância única da classe (Singleton).
			title (str): Título da janela de diálogo.
			textSenderName (wx.TextCtrl): Campo de entrada para o nome do remetente.
			textSubject (wx.TextCtrl): Campo de entrada para o assunto.
			textMessage (wx.TextCtrl): Campo de entrada para o texto do recado.
			textDate (wx.TextCtrl): Campo de entrada para a data da viagem.
			textTime (wx.TextCtrl): Campo de entrada para o horário da viagem.
			textPoint (wx.TextCtrl): Campo de entrada para o ponto de encontro.
			textPhone (wx.TextCtrl): Campo de entrada para o telefone do remetente.
			save_button (wx.Button): Botão para salvar a mensagem.
			clean_button (wx.Button): Botão para limpar os campos.
			cancel_button (wx.Button): Botão para cancelar e fechar o diálogo.

	Métodos:
			__new__(cls, *args, **kwargs): Implementa o padrão Singleton, garantindo uma única instância da classe.
			__init__(self, parent, title): Inicializa a janela de diálogo e seus componentes gráficos.
			InitUI(self): Configura os elementos da interface do usuário, como rótulos, caixas de entrada e botões.
	"""

	_instance = None

	def __new__(cls, *args, **kwargs):
		# Make this a singleton.
		if MessageForTransport._instance is None:
			return super(MessageForTransport, cls).__new__(cls, *args, **kwargs)
		return MessageForTransport._instance

	def __init__(self, parent, title):
		if MessageForTransport._instance is not None:
			return
		MessageForTransport._instance = self

		# translators: Title of contact list dialog.
		self.title = title

		# Window size definition
		WIDTH = 800
		HEIGHT = 800

		super(MessageForTransport, self).__init__(
			parent,
			title=title,
			size=(WIDTH, HEIGHT),
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
		)
		self.Bind(wx.EVT_WINDOW_DESTROY, self._onInternalDestroy)

		# Layout
		panel = wx.Panel(self)
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		viewFieldsBox = wx.BoxSizer(wx.VERTICAL)
		viewButtonBox = wx.BoxSizer(wx.HORIZONTAL)

		# Nome do remetente
		self.labelName = wx.StaticText(panel, label=_("Sender: "))
		self.textSenderName = wx.TextCtrl(panel, value="", size=(300, -1))
		viewFieldsBox.Add(self.labelName, flag=wx.TOP | wx.LEFT, border=5)
		viewFieldsBox.Add(
			self.textSenderName,
			flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
			border=5,
		)

		# Assunto
		self.labelSubject = wx.StaticText(panel, label=_("Subject: "))
		self.textSubject = wx.TextCtrl(panel, value="Recado para o transporte", size=(300, -1))
		viewFieldsBox.Add(
			self.textSubject,
			flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
			border=5,
		)
		viewFieldsBox.Add(self.labelSubject, flag=wx.TOP | wx.LEFT, border=5)

		# Texto do recado
		self.labelPatient = wx.StaticText(panel, label=_("Patient: "))
		self.textPatient = wx.TextCtrl(
			panel,
			style=wx.TE_MULTILINE,
			size=(300, 150),
		)
		viewFieldsBox.Add(self.labelPatient, flag=wx.TOP | wx.LEFT, border=5)
		viewFieldsBox.Add(
			self.textPatient,
			flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
			border=5,
		)

		# Travel date
		self.labelDate = wx.StaticText(panel, label=_("Travel date: "))
		self.textDate = MaskedTextCtrl(panel, MASK_DATE, size=(250, -1))
		viewFieldsBox.Add(self.labelDate, flag=wx.TOP | wx.LEFT, border=5)
		viewFieldsBox.Add(
			self.textDate,
			flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
			border=5,
		)

		# Horário da viagem
		self.labelTime = wx.StaticText(panel, label=_("Time of Travel: "))
		self.textTime = MaskedTextCtrl(panel, MASK_TIME, size=(250, -1))
		viewFieldsBox.Add(self.labelTime, flag=wx.TOP | wx.LEFT, border=5)
		viewFieldsBox.Add(
			self.textTime,
			flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
			border=5,
		)

		# Cidade de destino
		self.labelCity = wx.StaticText(panel, label=_("City: "))
		self.textCity = wx.TextCtrl(panel, -1, size=(250, -1))
		viewFieldsBox.Add(self.labelCity, flag=wx.TOP | wx.LEFT, border=5)
		viewFieldsBox.Add(
			self.textCity,
			flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
			border=5,
		)

		# Ponto de espera
		self.labelPoint = wx.StaticText(panel, label=_("Point: "))
		self.textPoint = wx.TextCtrl(panel, size=(250, 25))
		viewFieldsBox.Add(self.labelPoint, flag=wx.TOP | wx.LEFT, border=5)
		viewFieldsBox.Add(
			self.textPoint,
			flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
			border=5,
		)

		# Telefone do remetente
		self.labelPhone = wx.StaticText(panel, label=_("Sender's phone: "))
		self.textPhone = MaskedTextCtrl(panel, MASK_PHONE, size=(300, -1))
		self.textPhone.Bind(wx.EVT_CHAR_HOOK, self.onPasteAndClean)
		viewFieldsBox.Add(self.labelPhone, flag=wx.TOP | wx.LEFT, border=5)
		viewFieldsBox.Add(
			self.textPhone,
			flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
			border=5,
		)

		# Botão para Salvar o recado
		self.saveButton = wx.Button(panel, label=_("Save & message"))
		self.saveButton.Bind(wx.EVT_BUTTON, self.OnSave)
		viewButtonBox.Add(
			self.saveButton,
			flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM,
			border=10,
		)

		# Botão para limpar os campos
		self.cleanButton = wx.Button(panel, label=_("C&lean"))
		self.cleanButton.Bind(wx.EVT_BUTTON, self.onClean)
		viewButtonBox.Add(
			self.cleanButton,
			flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM,
			border=10,
		)

		# Botão para cancelar o diálogo
		self.cancelButton = wx.Button(panel, wx.ID_CANCEL, label=_("&Cancel"))
		self.cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)
		viewButtonBox.Add(
			self.cancelButton,
			flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM,
			border=10,
		)

		mainSizer.Add(viewFieldsBox, flag=wx.EXPAND | wx.ALL, border=10)
		mainSizer.Add(
			viewButtonBox,
			flag=wx.ALIGN_CENTER | wx.TOP,
			border=10,
		)
		# Aplicando o sizer principal no painel
		panel.SetSizerAndFit(mainSizer)

	def OnSave(self, event):
		"""
		Salva a mensagem digitada em um arquivo de texto na pasta "Documentos" do usuário.

		Args:
				event (wx.Event): Evento disparado ao acionar a função de salvar.

		Comportamento:
				- Obtém os valores dos campos de entrada.
				- Formata a mensagem com informações adicionais, como data e horário da gravação.
				- Gera um nome de arquivo baseado no assunto e no timestamp atual.
				- Salva o conteúdo no arquivo dentro da pasta "Documentos".
				- Exibe uma mensagem de sucesso ou erro conforme o resultado da operação.
				- Após salvar, limpa os campos do formulário chamando `onClean`.
		"""

		# Obtendo os valores dos campos
		name = self.textSenderName.GetValue()
		subject = self.textSubject.GetValue()
		patient = self.textPatient.GetValue()
		date = self.textDate.GetValue()
		time = self.textTime.GetValue()
		city = self.textCity.GetValue()
		point = self.textPoint.GetValue()
		phone = self.textPhone.GetValue()

		# Verifica se os campos obrigatórios estão vazios
		if self._areRequiredFieldsEmpty(name, subject, patient, city):
			return

		# Formata a mensagem
		recado = self._formatMessage(name, patient, date, time, city, point, phone)

		# Gera o caminho e nome do arquivo
		fileName = self._generateFileName(subject)

		# Tenta salvar o arquivo
		if self._saveMessageToFile(fileName, recado):
			self.showMessage(
				_("Saved message!"),
				_(
					"Success",
				),
				wx.OK | wx.ICON_INFORMATION,
			)
			self.onClean(event)
			self.onCancel(event)

	def _areRequiredFieldsEmpty(self, name, subject, patient, city):
		"""
		Verifica se os campos obrigatórios (Nome, Assunto e Mensagem) estão vazios.

		Args:
				name (str): Nome do remetente.
				subject (str): Assunto da mensagem.
				message (str): Texto da mensagem.

		Returns:
				bool: Retorna True se algum campo obrigatório estiver vazio, caso contrário, False.
		"""
		if any(field == "" for field in [name, subject, patient, city]):
			gui.messageBox(
				_("The Name, Subject, patient and city Fields cannot be null!"),
				_(
					"Attention",
				),
				wx.OK | wx.ICON_WARNING,
			)

			# Definir o foco no primeiro campo vazio
			if not name:
				self.textSenderName.SetFocus()
			elif not subject:
				self.textSubject.SetFocus()
			elif not patient:
				self.textPatient.SetFocus()
			elif not city:
				self.textCity.SetFocus()
			return True
		return False

	def _formatMessage(self, name, patient, date, time, city, point, phone):
		"""
		Formata a mensagem com os dados coletados.

		Args:
				name (str): Nome do remetente.
				message (str): Texto da mensagem.
				date (str): Data da viagem.
				time (str): Hora da viagem.
				city (str): Cidade de destino.
				point (str): Ponto de encontro.
				phone (str): Telefone do remetente.

		Returns:
				str: A mensagem formatada.
		"""
		timestamp = datetime.now().strftime("%H:%M %d/%m/%Y")
		if phone == "(__) _____-____":
			return f"{name} solicitou o cancelamento da viagem agendada para {patient} marcada para o dia {date} às {time}, com destino à cidade de {city}.\nPonto: {point}\n\nAvisado por {name} às {timestamp}\n"
		else:
			return f"{name} solicitou o cancelamento da viagem agendada para {patient} marcada para o dia {date} às {time}, com destino à cidade de {city}.\nPonto: {point}\nContato: {phone}\n\nAvisado por {name} às {timestamp}\n"

	def _generateFileName(self, subject):
		"""
		Gera o nome do arquivo baseado no assunto e no timestamp atual.

		Args:
				subject (str): Assunto da mensagem.

		Returns:
				str: Nome do arquivo a ser salvo.
		"""
		caminhoDocumentos = os.path.join(
			os.environ["USERPROFILE"],
			"Documents",
		)
		codFile = datetime.now().strftime("%H-%M %d-%m-%Y")
		return os.path.join(caminhoDocumentos, f"{subject} {codFile}.txt" if subject else "recado.txt")

	def _saveMessageToFile(self, fileName, recado):
		"""
		Salva a mensagem no arquivo de texto.

		Args:
				file_name (str): Nome do arquivo onde a mensagem será salva.
				recado (str): A mensagem a ser salva no arquivo.

		Returns:
				bool: Retorna True se o salvamento for bem-sucedido, False caso contrário.
		"""
		try:
			with open(fileName, "a") as file:
				file.write(recado)
			return True
		except Exception as e:
			self.showMessage(
				_(
					"Error when saving message: {}".format(
						str(e),
					),
				),
				_("Error"),
				wx.OK | wx.ICON_ERROR,
			)
			return False

	def onClean(self, event):
		"""
		Limpa os campos de entrada do formulário.

		Args:
				event (wx.Event): Evento disparado ao acionar a limpeza dos campos.

		Comportamento:
				- Remove o conteúdo de todos os campos de texto listados.
				- Move o foco para o campo do remetente após a limpeza.
		"""
		textControls = [
			self.textSenderName,
			self.textSubject,
			self.textPatient,
			self.textTime,
			self.textDate,
			self.textCity,
			self.textPoint,
			self.textPhone,
		]

		# Percorre os campos efetuando a limpeza
		for ctrl in textControls:
			ctrl.Clear()

		self.textSubject.SetValue("Recado para o transporte")
		# Foca no campo do remetente
		self.textSenderName.SetFocus()

	def showMessage(self, message, caption=None, style=None):
		"""
		Displays a message to the user in a dialog box.

		Args:
			message (str): The message to be displayed.
			caption (str, optional): The title of the dialog box. The default is ("").
			style (int, optional): The style of the dialog box,
			combining flags like wx.OK,
			wx.CANCEL, wx.ICON_INFORMATION, etc. The default is wx.OK | wx.ICON_INFORMATION.
		"""

		if caption is None:
			caption = _("Attention")
		if style is None:
			style = wx.OK | wx.ICON_INFORMATION

		gui.messageBox(message, caption, style)

	def onCancel(self, event):
		"""
		Manipula o evento de cancelamento da janela.

		Args:
				event (wx.Event): Evento disparado quando o usuário cancela a ação.

		Comportamento:
				Fecha a janela atual ao ser chamado.
		"""
		self.Destroy()

	def onPasteAndClean(self, event):
		# Check if it is Ctrl+V
		if event.GetKeyCode() == ord("V") and event.ControlDown():
			# Get the currently focused field (the one that triggered the event)
			currentField = event.GetEventObject()

			# Open the Windows clipboard
			if not wx.TheClipboard.IsOpened():
				wx.TheClipboard.Open()
				data = wx.TextDataObject()
				success = wx.TheClipboard.GetData(data)
				wx.TheClipboard.Close()

				if success:
					clipboardText = data.GetText()
					# Remove all non-digit characters from the clipboard text
					cleanText = re.sub(r"\D", "", clipboardText)

					# Inserts only clean numbers in the focused field
					currentField.SetValue(cleanText)
					return  # Block the original "dirty" Ctrl+V

		# If it's not Ctrl+V, let other keys (arrows, numbers, backspace) pass
		event.Skip()

	def _onInternalDestroy(self, evt):
		# Clears the Singleton instance so that the next __new__ creates a new one
		MessageForTransport._instance = None
		evt.Skip()

# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

Created on: 07/02/2025
"""

import os
import sys
from datetime import datetime

import addonHandler
import gui
import wx.adv
from logHandler import log

from .varsConfig import ADDON_PATH, is64, mask_phone, ADDON_NAME

# Add the lib/ folder to sys.path (only once)
libFolder = "lib64" if is64 else "lib"
libPath = os.path.join(ADDON_PATH, libFolder)

if os.path.isdir(libPath) and libPath not in sys.path:
	sys.path.insert(0, libPath)

try:
	from maskedTextCtrl import MaskedTextCtrl
except ImportError as e:
	log.error(f"[{ADDON_NAME}] Error when importing internal library 'MaskedTextCtrl': {e}")
	raise ImportError(_("Mandatory Library Absent: MaskedTextCtrl"))

# Initialize translation support
addonHandler.initTranslation()


class GeneralMessage(wx.Dialog):
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

	def __init__(self, parent, title):
		# Title of contact list dialog.
		self.title = title

		# Window size definition
		WIDTH = 800
		HEIGHT = 800

		super(GeneralMessage, self).__init__(
			parent, title=title, size=(WIDTH, HEIGHT), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

		self.InitUI()

	def InitUI(self):
		panel = wx.Panel(self)

		# Layout
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		view_fields_box = wx.BoxSizer(wx.VERTICAL)
		view_button_box = wx.BoxSizer(wx.HORIZONTAL)

		# Nome do remetente
		self.labelName = wx.StaticText(panel, label=_("Sender: "))
		self.textSenderName = wx.TextCtrl(panel, value="", size=(300, -1))
		view_fields_box.Add(self.labelName, flag=wx.TOP | wx.LEFT, border=5)
		view_fields_box.Add(self.textSenderName, flag=wx.EXPAND |
							wx.LEFT | wx.RIGHT, border=5)

		# Assunto
		self.labelSubject = wx.StaticText(panel, label=_("Subject: "))
		self.textSubject = wx.TextCtrl(panel, value="", size=(300, -1))
		view_fields_box.Add(self.textSubject, flag=wx.EXPAND |
							wx.LEFT | wx.RIGHT, border=5)
		view_fields_box.Add(self.labelSubject, flag=wx.TOP | wx.LEFT, border=5)

		# Texto do recado
		self.labelMessage = wx.StaticText(panel, label=_("Message Text: "))
		self.textMessage = wx.TextCtrl(
			panel, style=wx.TE_MULTILINE, size=(300, 150))
		view_fields_box.Add(self.labelMessage, flag=wx.TOP | wx.LEFT, border=5)
		view_fields_box.Add(self.textMessage, flag=wx.EXPAND |
							wx.LEFT | wx.RIGHT, border=5)

		# Telefone do remetente
		self.labelPhone = wx.StaticText(panel, label=_("Sender's phone: "))
		self.textPhone = MaskedTextCtrl(panel, mask_phone, size=(300, -1))
		view_fields_box.Add(self.labelPhone, flag=wx.TOP | wx.LEFT, border=5)
		view_fields_box.Add(self.textPhone, flag=wx.EXPAND |
							wx.LEFT | wx.RIGHT, border=5)

		# Botão para Salvar o recado
		self.save_button = wx.Button(panel, label=_("Save & message"))
		self.save_button.Bind(wx.EVT_BUTTON, self.OnSave)
		view_button_box.Add(self.save_button, flag=wx.ALIGN_CENTER |
							wx.TOP | wx.BOTTOM, border=10)

		# Botão para limpar os campos
		self.clean_button = wx.Button(panel, label=_("C&lean"))
		self.clean_button.Bind(wx.EVT_BUTTON, self.onClean)
		view_button_box.Add(self.clean_button, flag=wx.ALIGN_CENTER |
							wx.TOP | wx.BOTTOM, border=10)

		# Botão para cancelar o diálogo
		self.cancel_button = wx.Button(panel, wx.ID_CANCEL, label=_("&Cancel"))
		self.cancel_button.Bind(wx.EVT_BUTTON, self.onCancel)
		view_button_box.Add(self.cancel_button, flag=wx.ALIGN_CENTER |
							wx.TOP | wx.BOTTOM, border=10)

		main_sizer.Add(view_fields_box, flag=wx.EXPAND | wx.ALL, border=10)
		main_sizer.Add(view_button_box, flag=wx.ALIGN_CENTER |
					   wx.TOP, border=10)
		# Aplicando o sizer principal no painel
		panel.SetSizerAndFit(main_sizer)

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
		message = self.textMessage.GetValue()
		phone = self.textPhone.GetValue()

		# Verifica se os campos obrigatórios estão vazios
		if self._are_required_fields_empty(name, subject, message):
			return

		# Formata a mensagem
		recado = self._format_message(name, message, phone)

		# Gera o caminho e nome do arquivo
		file_name = self._generate_file_name(subject)

		# Tenta salvar o arquivo
		if self._save_message_to_file(file_name, recado):
			self.show_message(_("Saved message!"), _(
				"Success"), wx.OK | wx.ICON_INFORMATION)
			self.onClean(event)

	def _are_required_fields_empty(self, name, subject, message):
		"""
		Verifica se os campos obrigatórios (Nome, Assunto e Mensagem) estão vazios.

		Args:
				name (str): Nome do remetente.
				subject (str): Assunto da mensagem.
				message (str): Texto da mensagem.

		Returns:
				bool: Retorna True se algum campo obrigatório estiver vazio, caso contrário, False.
		"""
		if any(field == "" for field in [name, subject, message]):
			gui.messageBox(_("The Name, Subject and Message Fields cannot be null!"), _(
				"Attention"), wx.OK | wx.ICON_WARNING)

			# Definir o foco no primeiro campo vazio
			if not name:
				self.textSenderName.SetFocus()
			elif not subject:
				self.textSubject.SetFocus()
			elif not message:
				self.textMessage.SetFocus()
			return True
		return False

	def _format_message(self, name, message, phone):
		"""
		Formata a mensagem com os dados coletados.

		Args:
				name (str): Nome do remetente.
				message (str): Texto da mensagem.
				phone (str): Telefone do remetente.

		Returns:
				str: A mensagem formatada.
		"""
		timestamp = datetime.now().strftime('%H:%M %d/%m/%Y')
		return f"{message}.\nContato: {phone}\n\nAvisado por {name} às {timestamp}\n"

	def _generate_file_name(self, subject):
		"""
		Gera o nome do arquivo baseado no assunto e no timestamp atual.

		Args:
				subject (str): Assunto da mensagem.

		Returns:
				str: Nome do arquivo a ser salvo.
		"""
		caminho_documentos = os.path.join(
			os.environ["USERPROFILE"], "Documents")
		cod_file = datetime.now().strftime('%H-%M %d-%m-%Y')
		return os.path.join(caminho_documentos, f"{subject} {cod_file}.txt" if subject else "recado.txt")

	def _save_message_to_file(self, file_name, recado):
		"""
		Salva a mensagem no arquivo de texto.

		Args:
				file_name (str): Nome do arquivo onde a mensagem será salva.
				recado (str): A mensagem a ser salva no arquivo.

		Returns:
				bool: Retorna True se o salvamento for bem-sucedido, False caso contrário.
		"""
		try:
			with open(file_name, "a") as file:
				file.write(recado)
			return True
		except Exception as e:
			self.show_message(_("Error when saving message: {}".format(
				str(e))), _("Error"), wx.OK | wx.ICON_ERROR)
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
		text_controls = [
			self.textSenderName,
			self.textSubject,
			self.textMessage,
			self.textPhone,
		]

		# Percorre os campos efetuando a limpeza
		for ctrl in text_controls:
			ctrl.Clear()

		# Foca no campo do remetente
		self.textSenderName.SetFocus()

	def show_message(self, message, caption=_("Attention"), style=wx.OK | wx.ICON_INFORMATION):
		"""
		Displays a message to the user in a dialog box.

		Args:
			message (str): The message to be displayed.
			caption (str, optional): The title of the dialog box. The default is ("").
			style (int, optional): The style of the dialog box,
			combining flags like wx.OK,
			wx.CANCEL, wx.ICON_INFORMATION, etc. The default is wx.OK | wx.ICON_INFORMATION.
		"""

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

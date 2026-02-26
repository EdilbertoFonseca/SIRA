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
import wx
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

# Initializes the translation
addonHandler.initTranslation()


class MedicalDischarge(wx.Dialog):
	"""
	Diálogo para o envio e armazenamento de altas médicas.

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

		super(MedicalDischarge, self).__init__(
			parent,
			title=title,
			size=(WIDTH, HEIGHT),
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
		)

		# Layout
		panel = wx.Panel(self)
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		view_fields_box = wx.BoxSizer(wx.VERTICAL)
		view_button_box = wx.BoxSizer(wx.HORIZONTAL)

		# Nome do Hospital
		self.labelHospital = wx.StaticText(panel, label=_("Hospital: "))
		self.textHospital = wx.TextCtrl(panel, value="", size=(300, -1))
		view_fields_box.Add(
			self.labelHospital,
			flag=wx.TOP | wx.LEFT,
			border=5,
		)
		view_fields_box.Add(
			self.textHospital,
			flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
			border=5,
		)

		# Paciente
		self.labelPaciente = wx.StaticText(panel, label=_("Patient: "))
		self.textPaciente = wx.TextCtrl(panel, value="", size=(300, -1))
		view_fields_box.Add(
			self.textPaciente,
			flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
			border=5,
		)
		view_fields_box.Add(
			self.labelPaciente,
			flag=wx.TOP | wx.LEFT,
			border=5,
		)

		# Quarto
		self.labelQuarto = wx.StaticText(panel, label=_("Hospital room: "))
		self.textQuarto = wx.TextCtrl(panel, value="", size=(300, -1))
		view_fields_box.Add(self.labelQuarto, flag=wx.TOP | wx.LEFT, border=5)
		view_fields_box.Add(
			self.textQuarto,
			flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
			border=5,
		)

		# Leito
		self.labelLeito = wx.StaticText(panel, label=_("Bed: "))
		self.textLeito = wx.TextCtrl(panel, value="", size=(300, -1))
		view_fields_box.Add(self.labelLeito, flag=wx.TOP | wx.LEFT, border=5)
		view_fields_box.Add(
			self.textLeito,
			flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
			border=5,
		)

		# Transporte
		self.labelTransporte = wx.StaticText(panel, label=_("Transporte: "))
		self.textTransporte = wx.TextCtrl(panel, size=(250, 25))
		view_fields_box.Add(
			self.labelTransporte,
			flag=wx.TOP | wx.LEFT,
			border=5,
		)
		view_fields_box.Add(
			self.textTransporte,
			flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
			border=5,
		)

		# Telefone do paciente
		self.labelContatoDoPaciente = wx.StaticText(
			panel,
			label=_("Patient contact: "),
		)
		self.textContatoDoPaciente = MaskedTextCtrl(
			panel,
			mask_phone,
			size=(300, -1),
		)
		view_fields_box.Add(
			self.labelContatoDoPaciente,
			flag=wx.TOP | wx.LEFT,
			border=5,
		)
		view_fields_box.Add(
			self.textContatoDoPaciente,
			flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
			border=5,
		)

		# Acompanhante
		self.labelAcompanhante = wx.StaticText(
			panel,
			label=_("Escort: "),
		)
		self.textAcompanhante = wx.TextCtrl(panel, value="", size=(300, -1))
		view_fields_box.Add(
			self.labelAcompanhante,
			flag=wx.TOP | wx.LEFT,
			border=5,
		)
		view_fields_box.Add(
			self.textAcompanhante,
			flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
			border=5,
		)

		# Telefone do Acompanhante
		self.labelContatoDoAcompanhante = wx.StaticText(
			panel,
			label=_("Escort contact: "),
		)
		self.textContatoDoAcompanhante = MaskedTextCtrl(
			panel,
			mask_phone,
			size=(300, -1),
		)
		view_fields_box.Add(
			self.labelContatoDoAcompanhante,
			flag=wx.TOP | wx.LEFT,
			border=5,
		)
		view_fields_box.Add(
			self.textContatoDoAcompanhante,
			flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
			border=5,
		)

		# Responsável pela alta
		self.labelResponsavelPelaAlta = wx.StaticText(
			panel,
			label=_("Responsible for discharge: "),
		)
		self.textResponsavelPelaAlta = wx.TextCtrl(panel, value="", size=(300, -1))
		view_fields_box.Add(
			self.labelResponsavelPelaAlta,
			flag=wx.TOP | wx.LEFT,
			border=5,
		)
		view_fields_box.Add(
			self.textResponsavelPelaAlta,
			flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
			border=5,
		)

		# Telefone do Responsável pela alta
		self.labelContatoDoResponsavelPelaAlta = wx.StaticText(
			panel,
			label=_("Contato do Responsible for discharge: "),
		)
		self.textContatoDoResponsavelPelaAlta = MaskedTextCtrl(
			panel,
			mask_phone,
			size=(300, -1),
		)
		view_fields_box.Add(
			self.labelContatoDoResponsavelPelaAlta,
			flag=wx.TOP | wx.LEFT,
			border=5,
		)
		view_fields_box.Add(
			self.textContatoDoResponsavelPelaAlta,
			flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
			border=5,
		)

		# Texto da observação
		self.labelObservação = wx.StaticText(panel, label=_("Observation: "))
		self.textObservação = wx.TextCtrl(
			panel,
			style=wx.TE_MULTILINE,
			size=(300, 150),
		)
		view_fields_box.Add(
			self.labelObservação,
			flag=wx.TOP | wx.LEFT,
			border=5,
		)
		view_fields_box.Add(
			self.textObservação,
			flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
			border=5,
		)

		# Botão para Salvar o recado
		self.save_button = wx.Button(panel, label=_("&Save"))
		self.save_button.Bind(wx.EVT_BUTTON, self.OnSave)
		view_button_box.Add(
			self.save_button,
			flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM,
			border=10,
		)

		# Botão para limpar os campos
		self.clean_button = wx.Button(panel, label=_("C&lean"))
		self.clean_button.Bind(wx.EVT_BUTTON, self.onClean)
		view_button_box.Add(
			self.clean_button,
			flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM,
			border=10,
		)

		# Botão para cancelar o diálogo
		self.cancel_button = wx.Button(panel, wx.ID_CANCEL, label=_("&Cancel"))
		self.cancel_button.Bind(wx.EVT_BUTTON, self.onCancel)
		view_button_box.Add(
			self.cancel_button,
			flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM,
			border=10,
		)

		main_sizer.Add(view_fields_box, flag=wx.EXPAND | wx.ALL, border=10)
		main_sizer.Add(
			view_button_box,
			flag=wx.ALIGN_CENTER | wx.TOP,
			border=10,
		)
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
		variables = {
			"hospital": self.textHospital.GetValue(),
			"paciente": self.textPaciente.GetValue(),
			"quarto": self.textQuarto.GetValue(),
			"leito": self.textLeito.GetValue(),
			"transporte": self.textTransporte.GetValue(),
			"contatoDoPaciente": self.textContatoDoPaciente.GetValue(),
			"acompanhante": self.textAcompanhante.GetValue(),
			"contatoDoAcompanhante": self.textContatoDoAcompanhante.GetValue(),
			"responsavelPelaAlta": self.textResponsavelPelaAlta.GetValue(),
			"contatoDoResponsavelPelaAlta": self.textContatoDoResponsavelPelaAlta.GetValue(),
			"observação": self.textObservação.GetValue(),
		}

		# Verifica se os campos obrigatórios estão vazios
		if self._are_required_fields_empty(variables):
			return

		# Formata a mensagem
		altaMedica = self._format_message(variables)

		# Gera o caminho e nome do arquivo
		file_name = self._generate_file_name(variables["hospital"])

		# Tenta salvar o arquivo
		if self._save_message_to_file(file_name, altaMedica):
			self.show_message(
				_("High Medical Saves successfully!"),
				_(
					"Attention",
				),
				wx.OK | wx.ICON_INFORMATION,
			)
			self.onClean(event)

	def _are_required_fields_empty(self, variables):
		empty_fields = [field for field, value in variables.items() if not value]
		if empty_fields:
			self.show_message(_("Fill in all fields!"), _("Attention"), wx.OK | wx.ICON_WARNING)
			self.focus_on_empty_field(empty_fields[0])
			return True
		return False

	def focus_on_empty_field(self, field):
		if field == "hospital":
			self.textHospital.SetFocus()
		elif field == "paciente":
			self.textPaciente.SetFocus()
		elif field == "observação":
			self.textObservação.SetFocus()
		elif field == "quarto":
			self.textQuarto.SetFocus()
		elif field == "leito":
			self.textLeito.SetFocus()
		elif field == "transporte":
			self.textTransporte.SetFocus()
		elif field == "contatoDoPaciente":
			self.textContatoDoPaciente.SetFocus()
		elif field == "acompanhante":
			self.textAcompanhante.SetFocus()
		elif field == "contatoDoAcompanhante":
			self.textContatoDoAcompanhante.SetFocus()
		elif field == "responsavelPelaAlta":
			self.textResponsavelPelaAlta.SetFocus()
		elif field == "contatoDoResponsavelPelaAlta":
			self.textContatoDoResponsavelPelaAlta.SetFocus()

	def _format_message(self, variables):
		"""
		Formata a mensagem com os dados coletados.

		Args:
						name (str): Nome do remetente.
						message (str): Texto da mensagem.
						date (str): Data da viagem.
						time (str): Hora da viagem.
						point (str): Ponto de encontro.
						phone (str): Telefone do remetente.

		Returns:
						str: A mensagem formatada.
		"""

		timestamp = datetime.now().strftime("%H:%M %d/%m/%Y")

		msg = f"""ALTA MÉDICA

Hospital {variables["hospital"]}
Paciente: {variables["paciente"]}
Observação: {variables["observação"]}
Quarto: {variables["quarto"]}
Leito: {variables["leito"]}
Transporte: {variables["transporte"]}
Contato: {variables["contatoDoPaciente"]}
Acompanhante: {variables["acompanhante"]}
Contato do acompanhante: {variables["contatoDoAcompanhante"]}

Avisado por {variables["responsavelPelaAlta"]} as {timestamp}.
Contato: {variables["contatoDoResponsavelPelaAlta"]}
"""

		return msg

	def _generate_file_name(self, hospital):
		"""
		Gera o nome do arquivo baseado no assunto e no timestamp atual.

		Args:
						subject (str): Assunto da mensagem.

		Returns:
						str: Nome do arquivo a ser salvo.
		"""

		caminho_documentos = os.path.join(
			os.environ["USERPROFILE"],
			"Documents",
		)
		cod_file = datetime.now().strftime("%H-%M %d-%m-%Y")
		return os.path.join(
			caminho_documentos,
			f"Alta médica - Hospital {hospital} {cod_file}.txt" if hospital else "Alta médica.txt",
		)

	def _save_message_to_file(self, file_name, altaMedica):
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
				file.write(altaMedica + "\n")
			return True
		except Exception as e:
			self.show_message(
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
		text_controls = [
			self.textHospital,
			self.textPaciente,
			self.textLeito,
			self.textQuarto,
			self.textTransporte,
			self.textContatoDoPaciente,
			self.textAcompanhante,
			self.textContatoDoAcompanhante,
			self.textObservação,
			self.textResponsavelPelaAlta,
			self.textContatoDoResponsavelPelaAlta,
		]

		# Percorre os campos efetuando a limpeza
		for ctrl in text_controls:
			ctrl.Clear()

		# Foca no campo hospital
		self.textHospital.SetFocus()

	def show_message(self, message, caption=None, style=None):
		"""
		Displays a message to the user in a dialog box.

		Args:
			message (str): The message to be displayed.
			caption (str, optional): The title of the dialog box. The default is ("").
			style (int, optional): The style of the dialog box,
			combining flags like wx.OK,
			wx.CANCEL, wx.ICON_INFORMATION, etc. The default is wx.OK | wx.ICON_INFORMATION.
		"""

		# Avoid function calls or complex expressions in default parameter values.
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

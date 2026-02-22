# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

Created on: 21/02/2025
"""

import wx
import winsound


class MaskedTextCtrl(wx.TextCtrl):
	MASK_CHAR = 'X'
	PLACEHOLDER_CHAR = '_'

	def __init__(self, parent, mask, *args, **kwargs):
		super().__init__(parent, *args, **kwargs)
		self.mask = mask
		self._is_updating = False
		self.Bind(wx.EVT_CHAR, self.on_char)
		self.Bind(wx.EVT_TEXT, self.on_text)
		self._init_value()

	def _init_value(self):
		"""Inicializa o campo com o placeholder da máscara."""
		placeholder = self._generate_placeholder()
		self.SetValue(placeholder)
		self.SetInsertionPoint(0)

	def _generate_placeholder(self):
		"""Gera uma string do tamanho da máscara com placeholders."""
		return ''.join(
			self.PLACEHOLDER_CHAR if c == self.MASK_CHAR else c
			for c in self.mask
		)

	def on_char(self, event):
		key_code = event.GetKeyCode()
		pos = self.GetInsertionPoint()
		value = self.GetValue()
		length = len(value)

		allowed_keys = {
			wx.WXK_BACK, wx.WXK_DELETE, wx.WXK_LEFT, wx.WXK_RIGHT,
			wx.WXK_HOME, wx.WXK_END, wx.WXK_NUMPAD_ENTER, wx.WXK_RETURN,
			wx.WXK_TAB
		}

		if key_code in allowed_keys:
			if key_code == wx.WXK_BACK:
				# Backspace: pula para a posição anterior de dígito válido
				new_pos = self._find_previous_editable_pos(pos)
				if new_pos is not None:
					self._replace_char(new_pos, self.PLACEHOLDER_CHAR)
					self.SetInsertionPoint(new_pos)
				return  # não chama event.Skip() para evitar comportamento padrão

			if key_code == wx.WXK_DELETE:
				# Delete: apaga o caractere na posição atual se for editável
				if pos < length and self.mask[pos] == self.MASK_CHAR:
					self._replace_char(pos, self.PLACEHOLDER_CHAR)
					self.SetInsertionPoint(pos)
				return

			# Outras teclas permitidas
			event.Skip()
			return

		try:
			char = chr(key_code)
		except ValueError:
			return

		if not char.isdigit():
			# bloqueia qualquer tecla que não seja dígito
			return

		# Tenta inserir o dígito na posição atual
		if pos >= length:
			# fim do texto, ignora
			return

		next_pos = self._find_next_editable_pos(pos)
		if next_pos is None:
			# não tem mais espaço para digitar
			return

		self._replace_char(next_pos, char)
		self.SetInsertionPoint(next_pos + 1)

	def on_text(self, event):
		if self._is_updating:
			return
		# Previne edição direta do valor, só aceita via on_char
		# Reaplica o valor para evitar colar texto errado
		self._is_updating = True
		try:
			value = self.GetValue()
			clean_value = self.get_clean_value()

			# Reconstrói o texto com máscara e clean_value
			new_value = self._apply_mask(clean_value)
			if value != new_value:
				self.SetValue(new_value)
				# Ajusta cursor para o próximo lugar editável
				next_pos = self._find_next_editable_pos(self.GetInsertionPoint())
				if next_pos is None:
					next_pos = len(new_value)
				self.SetInsertionPoint(next_pos)
			
			# Beep quando campo completo (sem placeholders)
			if self.PLACEHOLDER_CHAR not in new_value:
				winsound.MessageBeep()
		finally:
			self._is_updating = False

		event.Skip()

	def _replace_char(self, pos, char):
		"""Substitui caractere na posição pos por char."""
		value = list(self.GetValue())
		if 0 <= pos < len(value):
			value[pos] = char
			self.SetValue(''.join(value))

	def _find_next_editable_pos(self, pos):
		"""Encontra próximo índice editável (onde mask é MASK_CHAR) >= pos."""
		for i in range(pos, len(self.mask)):
			if self.mask[i] == self.MASK_CHAR:
				return i
		return None

	def _find_previous_editable_pos(self, pos):
		"""Encontra o índice editável anterior < pos."""
		for i in range(pos - 1, -1, -1):
			if self.mask[i] == self.MASK_CHAR:
				return i
		return None

	def _apply_mask(self, digits):
		"""Aplica máscara na string só de dígitos."""
		formatted = []
		digit_index = 0
		for char in self.mask:
			if char == self.MASK_CHAR:
				if digit_index < len(digits):
					formatted.append(digits[digit_index])
					digit_index += 1
				else:
					formatted.append(self.PLACEHOLDER_CHAR)
			else:
				formatted.append(char)
		return ''.join(formatted)

	def get_clean_value(self):
		"""Retorna o valor do campo só com dígitos."""
		return ''.join(
			c for c, m in zip(self.GetValue(), self.mask) if m == self.MASK_CHAR and c.isdigit()
		)

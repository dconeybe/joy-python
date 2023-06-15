from __future__ import annotations

from collections.abc import Container
import enum
import io
from typing import TextIO


class SourceReader:

  def __init__(self, f: TextIO, buffer_size: int | None = None) -> None:
    if buffer_size is not None and buffer_size <= 0:
      raise ValueError(f"invalid buffer size: {buffer_size}")

    self.f = f
    self.buffer_size = buffer_size if buffer_size is not None else 1024

    self._current_buffer = ""
    self._current_buffer_index = 0
    self._lexeme_buffers: list[str] = []
    self._lexeme_start_index = 0
    self._lexeme_end_index = 0
    self._eof = False

  def lexeme(self) -> str:
    if len(self._lexeme_buffers) == 0:
      return self._current_buffer[self._lexeme_start_index : self._lexeme_end_index]

    result = io.StringIO()
    result.write(self._lexeme_buffers[0][self._lexeme_start_index :])
    for i in range(1, len(self._lexeme_buffers)):
      result.write(self._lexeme_buffers[i])
    result.write(self._current_buffer[: self._lexeme_end_index])

    return result.getvalue()

  def _lexeme_length(self) -> int:
    if len(self._lexeme_buffers) == 0:
      return self._lexeme_end_index - self._lexeme_start_index

    lexeme_length = len(self._lexeme_buffers[0]) - self._lexeme_start_index
    for i in range(1, len(self._lexeme_buffers)):
      lexeme_length += len(self._lexeme_buffers[i])
    lexeme_length += self._lexeme_end_index

    return lexeme_length

  def eof(self) -> bool:
    return self._eof

  def read(
      self, accepted_characters: str | Container[str], mode: ReadMode, max_lexeme_length: int | None
  ) -> None:
    if self._eof:
      return

    if mode == ReadMode.APPEND:
      lexeme_length = self._lexeme_length()
    else:
      lexeme_length = 0
      self._lexeme_buffers = []
      self._lexeme_start_index = self._current_buffer_index
      self._lexeme_end_index = self._current_buffer_index

    while True:
      if max_lexeme_length is not None and lexeme_length >= max_lexeme_length:
        break

      if self._current_buffer_index == len(self._current_buffer):
        if lexeme_length > 0 and mode != ReadMode.SKIP:
          self._lexeme_buffers.append(self._current_buffer)
        self._current_buffer = self.f.read(self.buffer_size)
        self._current_buffer_index = 0
        if lexeme_length == 0:
          self._lexeme_start_index = 0
          self._lexeme_end_index = 0
        if len(self._current_buffer) == 0:
          self._eof = True
          break

      current_character = self._current_buffer[self._current_buffer_index]
      if current_character not in accepted_characters:
        break
      self._current_buffer_index += 1
      lexeme_length += 1

    self._lexeme_end_index = self._current_buffer_index
    if mode == ReadMode.SKIP:
      self._lexeme_start_index = self._current_buffer_index


@enum.unique
class ReadMode(enum.Enum):
  NORMAL = 1
  APPEND = 2
  SKIP = 3

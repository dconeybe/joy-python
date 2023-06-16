from __future__ import annotations

import enum
from typing import TextIO


class SourceReader:

  def __init__(self, f: TextIO, buffer_size: int | None = None) -> None:
    if buffer_size is not None and buffer_size <= 0:
      raise ValueError(f"invalid buffer size: {buffer_size}")

    self.f = f
    self.buffer_size = buffer_size if buffer_size is not None else 1024

    self._buffer = ""
    self._buffer_offset = 0
    self._lexeme = ""
    self._eof = False

  def lexeme(self) -> str:
    return self._lexeme

  def lexeme_length(self) -> int:
    return len(self._lexeme)

  def eof(self) -> bool:
    return self._eof

  def read(
      self,
      accepted_characters: str,
      mode: ReadMode,
      max_lexeme_length: int | None,
      invert_accepted_characters: bool = False,
  ) -> None:
    if self._eof:
      return

    if mode == ReadMode.APPEND:
      lexeme_length = len(self._lexeme)
    else:
      self._lexeme = ""
      lexeme_length = 0

    while True:
      if max_lexeme_length is not None and lexeme_length >= max_lexeme_length:
        break

      if self._buffer_offset == len(self._buffer):
        self._buffer = self.f.read(self.buffer_size)
        self._buffer_offset = 0
        if len(self._buffer) == 0:
          self._eof = True
          break

      current_character = self._buffer[self._buffer_offset]

      if invert_accepted_characters and current_character in accepted_characters:
        break
      elif not invert_accepted_characters and current_character not in accepted_characters:
        break

      self._buffer_offset += 1
      lexeme_length += 1
      if mode != ReadMode.SKIP:
        self._lexeme += current_character


@enum.unique
class ReadMode(enum.Enum):
  NORMAL = 1
  APPEND = 2
  SKIP = 3

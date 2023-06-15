from __future__ import annotations

from collections.abc import Container
import enum
from typing import TextIO


class SourceReader:

  def __init__(self, f: TextIO, buffer_size: int | None = None) -> None:
    if buffer_size is not None and buffer_size <= 0:
      raise ValueError(f"invalid buffer size: {buffer_size}")

    self.f = f
    self.buffer_size = buffer_size if buffer_size is not None else 1024

    self._buf = ""
    self._buf_index = 0
    self._lexeme_start_index = 0
    self._lexeme_end_index = 0
    self._eof = False

  def lexeme(self) -> str:
    return self._buf[self._lexeme_start_index : self._lexeme_end_index]

  def eof(self) -> bool:
    return self._eof

  def read(
      self, accepted_characters: str | Container[str], mode: ReadMode, max_lexeme_length: int | None
  ) -> None:
    if self._eof:
      return

    if self._buf_index == len(self._buf):
      self._buf = self.f.read(self.buffer_size)
      if len(self._buf) == 0:
        self._eof = True
        return
      self._buf_index = 0

    if mode != ReadMode.APPEND:
      self._lexeme_start_index = self._buf_index

    while True:
      if self._buf_index == len(self._buf):
        break
      current_character = self._buf[self._buf_index]
      if current_character not in accepted_characters:
        break
      self._buf_index += 1

    self._lexeme_end_index = self._buf_index
    if mode == ReadMode.SKIP:
      self._lexeme_start_index = self._lexeme_end_index


@enum.unique
class ReadMode(enum.Enum):
  NORMAL = 1
  APPEND = 2
  SKIP = 3

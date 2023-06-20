from __future__ import annotations

import enum
from typing import TextIO


class SourceReader:

  def __init__(self, f: TextIO, buffer_size: int | None = None) -> None:
    if buffer_size is not None and buffer_size <= 0:
      raise ValueError(f"invalid buffer size: {buffer_size}")

    self.f = f
    self.buffer_size = buffer_size if buffer_size is not None else 1024

    self._position = 0
    self._buffer = ""
    self._read_offset = 0
    self._lexeme_offset = 0
    self._lexeme_length = 0
    self._eof = False

  def lexeme(self) -> str:
    return self._buffer[self._lexeme_offset : self._lexeme_offset + self._lexeme_length]

  def lexeme_length(self) -> int:
    return self._lexeme_length

  def position(self) -> int:
    return self._position

  def eof(self) -> bool:
    return self._eof

  def read(
      self,
      accepted_characters: str,
      mode: ReadMode,
      max_lexeme_length: int | None,
      invert_accepted_characters: bool = False,
  ) -> None:
    if mode == ReadMode.APPEND:
      lexeme_length = self._lexeme_length
    else:
      self._lexeme_offset = self._read_offset
      self._lexeme_length = 0
      lexeme_length = 0

    while True:
      if max_lexeme_length is not None and lexeme_length >= max_lexeme_length:
        break

      current_character = self.peek()
      if len(current_character) == 0:
        self._read()
        break

      if invert_accepted_characters and current_character in accepted_characters:
        break
      elif not invert_accepted_characters and current_character not in accepted_characters:
        break

      # Actually _consume_ the character that we just "peeked" at.
      self._read()
      lexeme_length += 1

      if mode == ReadMode.SKIP:
        self._lexeme_offset += 1
      else:
        self._lexeme_length += 1

  def read_until_exact_match(
      self,
      match: str,
      mode: ReadMode,
  ) -> bool:
    if len(match) == 0:
      raise ValueError("the empty string is not a valid value for the text to match")

    if mode != ReadMode.APPEND:
      self._lexeme_offset = self._read_offset
      self._lexeme_length = 0

    expected_character_list = list(match)
    actual_character_list = []

    while True:
      read_character = self._read()
      if len(read_character) == 0:
        return False

      if mode == ReadMode.SKIP:
        self._lexeme_offset += 1
      else:
        self._lexeme_length += 1

      actual_character_list.append(read_character)
      if len(actual_character_list) > len(expected_character_list):
        del actual_character_list[0]

      if actual_character_list == expected_character_list:
        return True

  def peek(self, desired_num_characters: int | None = None) -> str:
    return self._read(advance_read_offset=False, desired_num_characters=desired_num_characters)

  def _read(
      self, advance_read_offset: bool = True, desired_num_characters: int | None = None
  ) -> str:
    if desired_num_characters is None:
      desired_num_characters = 1
    if desired_num_characters < 0:
      raise ValueError(
          "the desired number of characters must not be negative: " f"{desired_num_characters}"
      )

    if self._eof:
      return ""

    while self._read_offset + desired_num_characters > len(self._buffer):
      buffer_offset = min(self._read_offset, self._lexeme_offset)

      self._buffer = self._buffer[buffer_offset:]
      self._read_offset -= buffer_offset
      self._lexeme_offset -= buffer_offset
      del buffer_offset

      new_buffer = self.f.read(self.buffer_size)
      if len(new_buffer) == 0:
        del new_buffer
        if advance_read_offset:
          self._eof = True
        break

      self._buffer += new_buffer
      del new_buffer

    if self._read_offset == len(self._buffer):
      return ""

    read_characters = self._buffer[self._read_offset : self._read_offset + desired_num_characters]

    if advance_read_offset:
      self._read_offset += len(read_characters)
      self._position += len(read_characters)

    return read_characters


@enum.unique
class ReadMode(enum.Enum):
  NORMAL = 1
  APPEND = 2
  SKIP = 3

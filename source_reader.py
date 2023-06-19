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
    self._mark_accumulator: str | None = None
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
    if mode == ReadMode.APPEND:
      lexeme_length = len(self._lexeme)
    else:
      self._lexeme = ""
      lexeme_length = 0

    while True:
      if max_lexeme_length is not None and lexeme_length >= max_lexeme_length:
        break

      current_character = self._peek()
      if current_character is None:
        return

      if invert_accepted_characters and current_character in accepted_characters:
        break
      elif not invert_accepted_characters and current_character not in accepted_characters:
        break

      self._read()

      lexeme_length += 1

      if mode != ReadMode.SKIP:
        self._lexeme += current_character

  def mark(self) -> None:
    """
    Marks the current position.

    A subsequent call to reset() repositions this reader at the last marked position so that
    subsequent reads re-read the same characters.

    The general contract of mark is that the stream saves all the characters read after the call to
    mark() and stands ready to supply those same bytes again if and whenever reset() is called. It
    is valid to call mark() even once end-of-input is reached (i.e. eof() returns True).

    If a mark is already set then it is replaced by the new mark.
    """
    self._mark_accumulator = ""

  def unmark(self) -> None:
    """
    Removes the mark, if set, as if mark() had never been invoked.
    """
    self._mark_accumulator = None

  def reset(self) -> None:
    """
    Repositions this reader to the position at the time mark() was last called.

    The stream is reset to a state such that all the characters read since the most recent call to
    mark() will be resupplied to subsequent callers of read(), followed by any characters that
    otherwise would have been the next input data as of the time of the call to reset().

    If mark() was called at end-of-input (i.e. when eof() returned True) then reset() keeps the
    stream at the end-of-input (i.e. it effectively does nothing but clear the mark).

    Raises:
      ResetCalledWithoutMarkSetError: if no mark is set; this could be because (a) mark() has never
        been called, (b) because a previous invocation of reset() already "consumed" the mark, or
        (c) unmark() was called to clear the mark.
    """
    if self._mark_accumulator is None:
      raise self.ResetCalledWithoutMarkSetError("reset() called when the mark is not set")
    self._buffer = self._mark_accumulator + self._buffer[self._buffer_offset :]
    self._buffer_offset = 0
    self._lexeme = ""
    self._mark_accumulator = None
    self._eof = False

  def _peek(self) -> str | None:
    return self._read(advance_offset=False)

  def _read(self, advance_offset: bool = True) -> str | None:
    if self._eof:
      return None

    if self._buffer_offset == len(self._buffer):
      self._buffer = self.f.read(self.buffer_size)
      self._buffer_offset = 0
      if len(self._buffer) == 0:
        self._eof = True
        return None

    current_character = self._buffer[self._buffer_offset]
    if advance_offset:
      self._buffer_offset += 1
      if self._mark_accumulator is not None:
        self._mark_accumulator += current_character

    return current_character

  class ResetCalledWithoutMarkSetError(RuntimeError):
    pass


@enum.unique
class ReadMode(enum.Enum):
  NORMAL = 1
  APPEND = 2
  SKIP = 3

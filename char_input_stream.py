from __future__ import annotations

import dataclasses
from typing import TextIO


class CharInputStream:

  def __init__(self, f: TextIO, buffer_size: int | None = None) -> None:
    self.f = f
    self.buffer_size = buffer_size

    self._eof = False
    self._buffer: _ReadBuffer | None = None
    self._mark_buffer: _ReadBuffer | None = None
    self._mark_accumulator: str | None = None

  def read(self) -> str | None:
    """
    Reads a single character from the underlying stream.

    Returns:
      The single character read, or None if end-of-input was reached.
    """
    if self._mark_buffer is not None:
      read_character = self._mark_buffer.read()
      if read_character is not None:
        if self._mark_accumulator is not None:
          self._mark_accumulator += read_character
        return read_character
      self._mark_buffer = None

    if self._eof:
      return None

    if self._buffer is None or self._buffer.eof():
      buffer = self.f.read(self._effective_buffer_size())
      if len(buffer) == 0:
        self._eof = True
        return None
      self._buffer = _ReadBuffer(buffer)

    read_character = self._buffer.read()
    if self._mark_accumulator is not None:
      self._mark_accumulator += read_character

    return read_character

  def mark(self) -> None:
    """
    Marks the current position in this input stream.

    A subsequent call to reset() repositions this stream at the last marked position so that
    subsequent reads re-read the same data. This data is buffered without limit; therefore, unmark()
    should be called when the mark is no longer needed.

    If a mark has already been set then it is discarded and replaced by the new mark at the current
    position in this input stream.
    """
    self._mark_accumulator = ""

  def unmark(self) -> None:
    """
    Clears the mark set by the most recent call to mark().

    If no mark is set then this method does nothing and returns as if successful.
    """
    self._mark_accumulator = None

  def reset(self) -> None:
    """
    Repositions this stream to the position at the time mark() was last called.

    Raises:
      RuntimeError: if mark() has not been called to set a mark, or if unmark() was called to clear
        the mark set by the most recent invocation of mark().
    """
    if self._mark_accumulator is None:
      raise RuntimeError("reset() invoked without a mark set")

    if self._mark_buffer is None:
      self._mark_buffer = _ReadBuffer(self._mark_accumulator)
    else:
      self._mark_buffer = self._mark_buffer.with_prepended_text(self._mark_accumulator)

    self._mark_accumulator = None

  def _effective_buffer_size(self) -> int:
    buffer_size = self.buffer_size
    return buffer_size if buffer_size is not None else 1024


class _ReadBuffer:

  def __init__(self, text: str) -> None:
    self.text = text
    self.index = 0

  def with_prepended_text(self, text: str) -> _ReadBuffer:
    return _ReadBuffer(text + self.text[self.index :])

  def eof(self) -> bool:
    return self.index == len(self.text)

  def read(self) -> str | None:
    if self.index == len(self.text):
      return None
    read_character = self.text[self.index]
    self.index += 1
    return read_character

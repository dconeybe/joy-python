from collections.abc import Collection
import dataclasses
import io
from typing import TextIO


@dataclasses.dataclass
class SourceCharacter:
  c: str = ""
  line_number: int = -1
  column_number: int = -1


class SourceReader:

  def __init__(self, f: TextIO) -> None:
    self.f = f
    self._line_number = 1
    self._column_number = 1
    self._buf: str | None = None
    self._buf_index = -1
    self._buffered_char: SourceCharacter | None = None
    self._last_read_char: SourceCharacter | None = None

  def read(
      self, result: SourceCharacter | None = None, skip_chars: Collection[str] | None = None
  ) -> SourceCharacter | None:
    """
    Reads one character from the underlying stream.

    Args:
      result: The object into which to store the information about the character; the contents of
        this object are undefined if False is returned; if None, then a new SourceCharacter object
        will be created and used.
      skip_chars: Characters that will be skipped if encountered; these skipped characters still
        advance the column and line numbers. If None, then no characters will be skipped. A common
        use case for this argument is to skip whitespace between tokens.

    Returns:
      Information about the character, or None if end-of-input was reached.
    """
    buffered_char = self._buffered_char
    self._buffered_char = None
    if buffered_char is not None:
      self._last_read_char = buffered_char
      return buffered_char

    while True:
      if self._buf is None:
        self._buf = self.f.read(8192)
        self._buf_index = 0

      if len(self._buf) == 0:
        self._last_read_char = None
        self._buffered_char = None
        return None

      c = self._buf[self._buf_index]
      self._buf_index += 1

      if self._buf_index == len(self._buf):
        self._buf = None
        self._buf_index = -1

      if self._last_read_char is not None and self._last_read_char.c == "\r" and c != "\n":
        self._line_number += 1
        self._column_number = 1

      if result is None:
        result = SourceCharacter()

      result.c = c
      result.line_number = self._line_number
      result.column_number = self._column_number
      self._column_number += 1

      if c == "\n":
        self._line_number += 1
        self._column_number = 1

      self._last_read_char = result

      if skip_chars and c in skip_chars:
        continue

      return result

  def unread(self) -> None:
    """
    Unreads the last character that was returned from read().

    Note that the exact object returned from the last invocation of read() will be returned from the
    next invocation of read(). Therefore, if any changes are made to the object returned from the
    last invocation of read() then they will be reflected in the object returned from the next
    invocation of read().

    Invoking this method after read() has returned None has no effect.

    Raises:
      RuntimeError: if invoked when there is no character to unread, such as before the first
        invocation of read() or the object returned from the last invocation of read() has already
        been unread.
    """
    if self._last_read_char is None:
      if self._buf is None:
        raise RuntimeError("unread() must not be invoked until read() is invoked at least once")
      elif len(self._buf) == 0:
        return  # Do nothing if invoked after EOF, as documented.
      else:
        raise RuntimeError(
            "unread() must not be invoked multiple times"
            "without an interleaving invocation of read()"
        )

    self._buffered_char = self._last_read_char
    self._last_read_char = None


@dataclasses.dataclass
class Token:
  start_line_number: int = -1
  end_line_number: int = -1
  start_column_number: int = -1
  end_column_number: int = -1
  identifier: str = ""


_WHITESPACE_CHARS = frozenset("\r\n\t ")
_IDENTIFIER_CHARS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
_IDENTIFIER_INVALID_FIRST_CHARS = frozenset("0123456789")


class Tokenizer:

  def __init__(self, source_reader: SourceReader) -> None:
    self.source_reader = source_reader

  def next(self, token: Token | None = None) -> Token | None:
    """
    Reads a token from the source.

    Args:
      token: The object into which to populate the token's information; the state of this object is
        undefined if None is returned; if None, a new Token object will be created and used.

    Returns:
      The parsed token, or None if the end of input was reached.

    Raises:
      TokenError: If a parsing error occurs.
    """
    if token is None:
      token = Token()

    c: SourceCharacter | None = None
    last_line_number = -1
    last_column_number = -1
    buf = io.StringIO()
    buf_size = 0

    while True:
      if c is not None:
        last_line_number = c.line_number
        last_column_number = c.column_number

      c = self.source_reader.read(c)
      if c is None:
        break

      if c.c in _WHITESPACE_CHARS:
        if buf_size > 0:
          break
      elif c.c in _IDENTIFIER_CHARS:
        if buf_size == 0:
          if c.c in _IDENTIFIER_INVALID_FIRST_CHARS:
            raise self.TokenError(
                c.line_number, c.column_number, f"invalid character to start an identifier: {c.c}"
            )
          token.start_line_number = c.line_number
          token.start_column_number = c.column_number

        buf.write(c.c)
        buf_size += 1
      else:
        raise self.TokenError(c.line_number, c.column_number, f"illegal character: {c.c}")

    if buf_size == 0:
      return None

    token.end_line_number = last_line_number
    token.end_column_number = last_column_number
    token.identifier = buf.getvalue()
    return token

  class TokenError(Exception):

    def __init__(self, line_number: int, column_number: int, message: str) -> None:
      super().__init__(message)
      self.line_number = line_number
      self.column_number = column_number

from __future__ import annotations

import source_reader as source_reader_module

_WHITESPACE_CHARS = " \n\r\t"
_IDENTIFIER_START_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
_IDENTIFIER_SUBSEQUENT_CHARS = _IDENTIFIER_START_CHARS + "0123456789"
_MAX_IDENTIFIER_LENGTH = 256


class Tokenizer:

  def __init__(self, source_reader: source_reader_module.SourceReader) -> None:
    self.source_reader = source_reader

    self._token: str | None = None

  def token(self) -> str | None:
    return self._token

  def eof(self) -> bool:
    return self.source_reader.eof()

  def read(self) -> None:
    self._token = None

    # Skip leading whitespace
    self.source_reader.read(
        accepted_characters=_WHITESPACE_CHARS,
        mode=source_reader_module.ReadMode.SKIP,
        max_lexeme_length=None,
    )

    if self.source_reader.eof():
      return

    # Read the first character(s) of an identifier
    self.source_reader.read(
        accepted_characters=_IDENTIFIER_START_CHARS,
        mode=source_reader_module.ReadMode.NORMAL,
        max_lexeme_length=1,
    )

    if self.source_reader.lexeme_length() == 0:
      raise self.ParseError("invalid identifier")

    # Read the subsequent character(s) of an identifier
    self.source_reader.read(
        accepted_characters=_IDENTIFIER_SUBSEQUENT_CHARS,
        mode=source_reader_module.ReadMode.APPEND,
        max_lexeme_length=_MAX_IDENTIFIER_LENGTH + 1,
    )

    lexeme = self.source_reader.lexeme()
    if len(lexeme) > _MAX_IDENTIFIER_LENGTH:
      raise self.ParseError(
          f"identifier exceeds maximum length of {_MAX_IDENTIFIER_LENGTH}: {lexeme}"
      )

    self._token = lexeme

  class ParseError(Exception):
    pass

from __future__ import annotations

import source_reader as source_reader_module

_WHITESPACE_CHARS = " \n\r\t"
_IDENTIFIER_START_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
_IDENTIFIER_SUBSEQUENT_CHARS = _IDENTIFIER_START_CHARS + "0123456789"
_MAX_IDENTIFIER_LENGTH = 256


class Tokenizer:

  def __init__(self, source_reader: source_reader_module.SourceReader) -> None:
    self.source_reader = source_reader

  def eof(self) -> bool:
    return self.source_reader.eof()

  def read_identifier(self) -> str | None:
    self._skip_whitespace_and_comments()

    # Read the first character(s) of an identifier
    self.source_reader.read(
        accepted_characters=_IDENTIFIER_START_CHARS,
        mode=source_reader_module.ReadMode.NORMAL,
        max_lexeme_length=1,
    )

    # Fail if an invalid identifier start character was encountered.
    if self.source_reader.lexeme_length() == 0:
      if self.source_reader.eof():
        return None

      self.source_reader.read(
          accepted_characters=_WHITESPACE_CHARS,
          mode=source_reader_module.ReadMode.NORMAL,
          max_lexeme_length=20,
          invert_accepted_characters=True,
      )
      invalid_identifer = self.source_reader.lexeme()
      raise self.InvalidIdentifierError(
          identifier=invalid_identifer,
          message=f"invalid identifier: {self.source_reader.lexeme()}",
      )

    # Read the subsequent character(s) of an identifier
    self.source_reader.read(
        accepted_characters=_IDENTIFIER_SUBSEQUENT_CHARS,
        mode=source_reader_module.ReadMode.APPEND,
        max_lexeme_length=_MAX_IDENTIFIER_LENGTH + 1,
    )

    identifier = self.source_reader.lexeme()
    if len(identifier) > _MAX_IDENTIFIER_LENGTH:
      raise self.IdentifierTooLongError(
          identifier=identifier,
          max_length=_MAX_IDENTIFIER_LENGTH,
          message=f"identifier exceeds maximum length of {_MAX_IDENTIFIER_LENGTH}: {identifier}",
      )

    return identifier

  def _skip_whitespace_and_comments(self) -> None:
    while True:
      # Skip whitespace.
      self.source_reader.read(
          accepted_characters=_WHITESPACE_CHARS,
          mode=source_reader_module.ReadMode.SKIP,
          max_lexeme_length=None,
      )

      # Read the next two characters, which potentially start a comment
      self.source_reader.mark()
      self.source_reader.read(
          accepted_characters="/*",
          mode=source_reader_module.ReadMode.NORMAL,
          max_lexeme_length=2,
      )

      # If a comment is starting, then skip it; otherwise, we're done.
      match self.source_reader.lexeme():
        case "//":
          self.source_reader.unmark()
          self._skip_inline_comment()
        case "/*":
          self.source_reader.unmark()
          self._skip_multiline_comment()
        case _:
          self.source_reader.reset()
          break

  def _skip_inline_comment(self) -> None:
    self.source_reader.read(
        accepted_characters="\r\n",
        mode=source_reader_module.ReadMode.SKIP,
        max_lexeme_length=None,
        invert_accepted_characters=True,
    )

  def _skip_multiline_comment(self) -> None:
    while True:
      self.source_reader.read(
          accepted_characters="*",
          mode=source_reader_module.ReadMode.SKIP,
          max_lexeme_length=None,
          invert_accepted_characters=True,
      )

      self.source_reader.read(
          accepted_characters="*",
          mode=source_reader_module.ReadMode.NORMAL,
          max_lexeme_length=1,
      )

      self.source_reader.mark()
      self.source_reader.read(
          accepted_characters="/",
          mode=source_reader_module.ReadMode.NORMAL,
          max_lexeme_length=1,
      )

      if self.source_reader.lexeme() == "/":
        self.source_reader.unmark()
        break

      if self.source_reader.eof():
        raise self.UnterminatedMultiLineCommentError()

      self.source_reader.reset()

  class ParseError(Exception):
    pass

  class InvalidIdentifierError(ParseError):

    def __init__(self, identifier: str, message: str) -> None:
      super().__init__(message)
      self.identifier = identifier

  class IdentifierTooLongError(ParseError):

    def __init__(self, identifier: str, max_length: int, message: str) -> None:
      super().__init__(message)
      self.identifier = identifier
      self.max_length = max_length

  class UnterminatedMultiLineCommentError(ParseError):
    pass

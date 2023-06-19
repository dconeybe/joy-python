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
      if self.source_reader.eof():
        break

      # Skip whitespace.
      self.source_reader.read(
          accepted_characters=_WHITESPACE_CHARS,
          mode=source_reader_module.ReadMode.SKIP,
          max_lexeme_length=None,
      )

      # If a comment is starting, then skip it.
      potential_comment_starter = self.source_reader.peek(desired_num_characters=2)
      match potential_comment_starter:
        case "//":
          self.source_reader.read(
              accepted_characters="\r\n",
              mode=source_reader_module.ReadMode.SKIP,
              max_lexeme_length=None,
              invert_accepted_characters=True,
          )
        case "/*":
          self.source_reader.read_until_exact_match("*/", mode=source_reader_module.ReadMode.SKIP)
        case _:
          break

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

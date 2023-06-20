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
    # Read the first character(s) of an identifier
    self.source_reader.read(
        accepted_characters=_IDENTIFIER_START_CHARS,
        mode=source_reader_module.ReadMode.NORMAL,
        max_lexeme_length=1,
    )

    if self.source_reader.lexeme_length() == 0:
      return None

    # Read the subsequent character(s) of the identifier
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

  def skip_whitespace(self) -> bool:
    character_read_count = self.source_reader.read(
        accepted_characters=_WHITESPACE_CHARS,
        mode=source_reader_module.ReadMode.SKIP,
        max_lexeme_length=None,
    )
    return character_read_count > 0

  def skip_inline_comment(self) -> bool:
    potential_comment_starter = self.source_reader.peek(desired_num_characters=2)
    if potential_comment_starter != "//":
      return False

    self.source_reader.read(
        accepted_characters="\r\n",
        mode=source_reader_module.ReadMode.SKIP,
        max_lexeme_length=None,
        invert_accepted_characters=True,
    )
    return True

  def skip_multiline_comment(self) -> bool:
    potential_comment_starter = self.source_reader.peek(desired_num_characters=2)
    if potential_comment_starter != "/*":
      return False

    self.source_reader.read_until_exact_match("*/", mode=source_reader_module.ReadMode.SKIP)
    return True

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

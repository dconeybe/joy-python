from __future__ import annotations

import dataclasses

import tokenizer as tokenizer_module


class Parser:

  def __init__(self, tokenizer: tokenizer_module.Tokenizer) -> None:
    self.tokenizer = tokenizer
    self.functions: list[JoyFunction] = []

  def parse(self) -> None:
    state = "top"
    function_name = ""
    accumulated_annotations: list[str] = []

    while True:
      if self.tokenizer.eof():
        break

      self.tokenizer.skip_whitespace()
      self.tokenizer.skip_inline_comment()
      self.tokenizer.skip_multiline_comment()

      match state:
        case "top":
          identifier = self.tokenizer.read_identifier()
          if identifier == "function":
            state = "function_name"
          elif identifier is not None:
            raise self.ParseError(f"expected 'function' but got {identifier}")
          del identifier
        case "function_name":
          function_name = self.tokenizer.read_identifier()
          if function_name is None:
            raise self.ParseError("expected a function name following the 'function' keyword")
          self.functions.append(JoyFunction(name=function_name, annotations=tuple()))
          state = "top"

  class ParseError(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class JoyFunction:
  # The name of the function (e.g. "doSomething", "main").
  name: str
  # The annotations applied to the function.
  annotations: tuple[str, ...]

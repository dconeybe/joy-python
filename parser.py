from __future__ import annotations

import dataclasses

import tokenizer as tokenizer_module


class Parser:

  def __init__(self, tokenizer: tokenizer_module.Tokenizer) -> None:
    self.tokenizer = tokenizer
    self.functions: list[JoyFunction] = []

  def parse(self) -> None:
    while True:
      identifier = self.tokenizer.read_identifier()
      if identifier is None:
        assert self.tokenizer.eof()
        break  # end-of-file

      if identifier != "function":
        raise self.ParseError(f"expected 'function' got got {identifier}")

      function_name = self.tokenizer.read_identifier()
      if identifier is None:
        assert self.tokenizer.eof()
        raise self.ParseError(f"expected function name after {identifier}")

      self.functions.append(JoyFunction(name=function_name))

  class ParseError(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class JoyFunction:
  # The name of the function (e.g. "doSomething", "main").
  name: str

from __future__ import annotations

import dataclasses

import tokenizer as tokenizer_module


class Parser:

  def __init__(self, tokenizer: tokenizer_module.Tokenizer) -> None:
    self.tokenizer = tokenizer
    self.functions = list[JoyFunction]

  def parse(self) -> None:
    pass


@dataclasses.dataclass(frozen=True)
class JoyFunction:
  # The name of the function (e.g. "doSomething", "main").
  name: str

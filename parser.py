from __future__ import annotations

from collections.abc import Generator
import dataclasses

import tokenizer as tokenizer_module


class Parser:

  def __init__(self, tokenizer: tokenizer_module.Tokenizer) -> None:
    self.tokenizer = tokenizer
    self.functions: list[JoyFunction] = []

  def parse(self) -> None:
    parser = self._parse()

    while True:
      if self.tokenizer.eof():
        break

      if self.tokenizer.skip_whitespace():
        continue
      if self.tokenizer.skip_inline_comment():
        continue
      if self.tokenizer.skip_multiline_comment():
        continue

      parser.send(None)

    parser.close()

  def _parse(self) -> Generator[None, None, None]:
    accumulated_annotations: list[str] = []

    while True:
      try:
        yield
      except GeneratorExit:
        if len(accumulated_annotations) > 0:
          raise self.ParseError(
              "end-of-file reached unexpectedly after annotations: "
              f"{' ,'.join(accumulated_annotations)}"
          )
        raise

      annotation = self.tokenizer.read_annotation()
      if annotation is not None:
        accumulated_annotations.append(annotation)
        continue

      identifier = self.tokenizer.read_identifier()
      if identifier is None:
        raise self.ParseError("expected function declaration")
      if identifier != "function":
        raise self.ParseError(f"expected `function` but got {identifier}")
      try:
        yield
        function_name = self.tokenizer.read_identifier()
        if function_name is None:
          raise self.ParseError("expected function name after `function` keyword")
      except GeneratorExit:
        raise self.ParseError("end-of-file reached unexpectedly in function definition")

      self.functions.append(
          JoyFunction(name=function_name, annotations=tuple(accumulated_annotations))
      )
      accumulated_annotations = []

  class ParseError(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class JoyFunction:
  # The name of the function (e.g. "doSomething", "main").
  name: str
  # The annotations applied to the function.
  annotations: tuple[str, ...]

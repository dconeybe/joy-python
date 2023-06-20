import io

from absl.testing import absltest

import parser as parser_module
import source_reader as source_reader_module
import tokenizer as tokenizer_module

JoyFunction = parser_module.JoyFunction
Parser = parser_module.Parser
SourceReader = source_reader_module.SourceReader
Tokenizer = tokenizer_module.Tokenizer


class ParserTest(absltest.TestCase):

  def test_init(self):
    Parser(self.create_tokenizer(""))

  def test_parse_functions(self):
    parser = self.create_parser(
        """
          function abc
          function def
          function _12
        """
    )

    parser.parse()

    self.assertEqual(
        [
            JoyFunction(name="abc", annotations=tuple()),
            JoyFunction(name="def", annotations=tuple()),
            JoyFunction(name="_12", annotations=tuple()),
        ],
        parser.functions,
    )

  def test_parse_function_annotations(self):
    parser = self.create_parser(
        """
          @main
          function aaa
          @abc function def @def @ghi @jkl
          function _12
          @zzz // an interleaving inline coment
          @yyy /* an interleaving multiline comment
          */function bbb
        """
    )

    parser.parse()

    self.assertEqual(
        [
            JoyFunction(name="aaa", annotations=("main",)),
            JoyFunction(name="def", annotations=("abc",)),
            JoyFunction(name="_12", annotations=("def", "ghi", "jkl")),
            JoyFunction(name="bbb", annotations=("zzz", "yyy")),
        ],
        parser.functions,
    )

  def create_tokenizer(self, text: str) -> Tokenizer:
    return Tokenizer(source_reader=SourceReader(io.StringIO(text)))

  def create_parser(self, text: str) -> Parser:
    return Parser(self.create_tokenizer(text))


if __name__ == "__main__":
  absltest.main()

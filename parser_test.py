import io

from absl.testing import absltest

import parser as parser_module
import source_reader as source_reader_module
import tokenizer as tokenizer_module


Parser = parser_module.Parser
SourceReader = source_reader_module.SourceReader
Tokenizer = tokenizer_module.Tokenizer


class ParserTest(absltest.TestCase):

  def test_init(self):
    Parser(self.create_tokenizer(""))

  def create_tokenizer(self, text: str) -> Tokenizer:
    return Tokenizer(source_reader=SourceReader(io.StringIO(text)))


if __name__ == "__main__":
  absltest.main()

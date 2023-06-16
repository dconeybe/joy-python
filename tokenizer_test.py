import io

from absl.testing import absltest

import source_reader as source_reader_module
import tokenizer as tokenizer_module


Tokenizer = tokenizer_module.Tokenizer


class TokenizerTest(absltest.TestCase):

  def test_token_on_new_instance_should_return_none(self):
    tokenizer = Tokenizer(source_reader=source_reader_module.SourceReader(io.StringIO("")))
    self.assertIsNone(tokenizer.token())

  def test_eof_on_new_instance_should_return_False(self):
    tokenizer = Tokenizer(source_reader=source_reader_module.SourceReader(io.StringIO("")))
    self.assertFalse(tokenizer.eof())

  def test_read_on_empty_source_should_immediately_go_to_eof(self):
    tokenizer = self.create_tokenizer("")

    tokenizer.read()

    self.assertIsNone(tokenizer.token())
    self.assertTrue(tokenizer.eof())

  def test_read_on_entirely_whitespace_source_should_immediately_go_to_eof(self):
    tokenizer = self.create_tokenizer("  \r\n\n\n\r\t  \t \r \n \t")

    tokenizer.read()

    self.assertIsNone(tokenizer.token())
    self.assertTrue(tokenizer.eof())

  def test_read_with_multiple_consecutive_identifiers(self):
    tokenizer = self.create_tokenizer("abc   def \na12\r\n b23")

    tokenizer.read()
    self.assertEqual("abc", tokenizer.token())
    self.assertFalse(tokenizer.eof())
    tokenizer.read()
    self.assertEqual("def", tokenizer.token())
    self.assertFalse(tokenizer.eof())
    tokenizer.read()
    self.assertEqual("a12", tokenizer.token())
    self.assertFalse(tokenizer.eof())
    tokenizer.read()
    self.assertEqual("b23", tokenizer.token())
    self.assertTrue(tokenizer.eof())

  def test_raises_on_numeric_start_character(self):
    tokenizer = self.create_tokenizer("1ab")

    with self.assertRaises(tokenizer.ParseError) as assert_raises_context:
      tokenizer.read()

    exception_message = str(assert_raises_context.exception)
    self.assertIn("invalid identifier", exception_message.lower())
    self.assertIn("1ab", exception_message)

  def test_raises_on_identifier_too_long(self):
    tokenizer = self.create_tokenizer("a" * 300)

    with self.assertRaises(tokenizer.ParseError) as assert_raises_context:
      tokenizer.read()

    exception_message = str(assert_raises_context.exception)
    self.assertIn("a" * 257, exception_message)
    self.assertIn("exceeds maximum length", exception_message.lower())
    self.assertIn("256", exception_message)
    self.assertIsNone(tokenizer.token())

  def create_tokenizer(self, text: str) -> Tokenizer:
    return Tokenizer(source_reader=source_reader_module.SourceReader(io.StringIO(text)))


if __name__ == "__main__":
  absltest.main()

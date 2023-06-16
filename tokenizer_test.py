import io

from absl.testing import absltest

import source_reader as source_reader_module
import tokenizer as tokenizer_module


Tokenizer = tokenizer_module.Tokenizer


class TokenizerTest(absltest.TestCase):

  def test_eof_on_new_instance_should_return_False(self):
    tokenizer = Tokenizer(source_reader=source_reader_module.SourceReader(io.StringIO("")))
    self.assertFalse(tokenizer.eof())

  def test_read_identifier_on_empty_source_should_immediately_go_to_eof(self):
    tokenizer = self.create_tokenizer("")

    read_identifier_result = tokenizer.read_identifier()

    self.assertIsNone(read_identifier_result)
    self.assertTrue(tokenizer.eof())

  def test_read_identifier_on_entirely_whitespace_source_should_immediately_go_to_eof(self):
    tokenizer = self.create_tokenizer("  \r\n\n\n\r\t  \t \r \n \t")

    read_identifier_result = tokenizer.read_identifier()

    self.assertIsNone(read_identifier_result)
    self.assertTrue(tokenizer.eof())

  def test_read_identifier_with_multiple_consecutive_identifiers(self):
    tokenizer = self.create_tokenizer("abc   def \na12\r\n b23")

    read_identifier_result1 = tokenizer.read_identifier()
    self.assertEqual("abc", read_identifier_result1)
    self.assertFalse(tokenizer.eof())
    read_identifier_result2 = tokenizer.read_identifier()
    self.assertEqual("def", read_identifier_result2)
    self.assertFalse(tokenizer.eof())
    read_identifier_result3 = tokenizer.read_identifier()
    self.assertEqual("a12", read_identifier_result3)
    self.assertFalse(tokenizer.eof())
    read_identifier_result4 = tokenizer.read_identifier()
    self.assertEqual("b23", read_identifier_result4)
    self.assertTrue(tokenizer.eof())

  def test_read_identifier_raises_on_numeric_start_character(self):
    tokenizer = self.create_tokenizer("1ab")

    with self.assertRaises(tokenizer.InvalidIdentifierError) as assert_raises_context:
      tokenizer.read_identifier()

    exception_message = str(assert_raises_context.exception)
    self.assertIn("invalid identifier", exception_message.lower())
    self.assertIn("1ab", exception_message)
    self.assertEqual(assert_raises_context.exception.identifier, "1ab")

  def test_read_identifier_raises_on_identifier_too_long(self):
    tokenizer = self.create_tokenizer("a" * 300)

    with self.assertRaises(tokenizer.IdentifierTooLongError) as assert_raises_context:
      tokenizer.read_identifier()

    exception_message = str(assert_raises_context.exception)
    self.assertIn("a" * 257, exception_message)
    self.assertIn("exceeds maximum length", exception_message.lower())
    self.assertIn("256", exception_message)
    self.assertEqual(assert_raises_context.exception.identifier, "a" * 257)
    self.assertEqual(assert_raises_context.exception.max_length, 256)

  def create_tokenizer(self, text: str) -> Tokenizer:
    return Tokenizer(source_reader=source_reader_module.SourceReader(io.StringIO(text)))


if __name__ == "__main__":
  absltest.main()

import io

from absl.testing import absltest

import source_reader as source_reader_module
import tokenizer as tokenizer_module


Tokenizer = tokenizer_module.Tokenizer


class TokenizerTest(absltest.TestCase):

  def test_eof_on_new_instance_should_return_False(self):
    tokenizer = Tokenizer(source_reader=source_reader_module.SourceReader(io.StringIO("")))
    self.assertFalse(tokenizer.eof())

  def test_read_identifier_on_empty_source_should_return_none_and_advance_to_eof(self):
    tokenizer = self.create_tokenizer("")

    return_value = tokenizer.read_identifier()

    self.assertIsNone(return_value)
    self.assertTrue(tokenizer.eof())

  def test_read_identifier_with_invalid_start_char_should_return_none(self):
    tokenizer = self.create_tokenizer("// This is not a valid identifier")

    return_value = tokenizer.read_identifier()

    self.assertIsNone(return_value)
    self.assertFalse(tokenizer.eof())
    self.assertTrue(tokenizer.skip_inline_comment())
    self.assertTrue(tokenizer.eof())

  def test_read_identifier_reads_a_single_character_identifier(self):
    tokenizer = self.create_tokenizer("a  ")

    return_value = tokenizer.read_identifier()

    self.assertEqual("a", return_value)
    self.assertFalse(tokenizer.eof())
    self.assertTrue(tokenizer.skip_whitespace())
    self.assertTrue(tokenizer.eof())

  def test_read_identifier_reads_a_single_character_identifier_to_eof(self):
    tokenizer = self.create_tokenizer("a")

    return_value = tokenizer.read_identifier()

    self.assertEqual("a", return_value)
    self.assertTrue(tokenizer.eof())

  def test_read_identifier_reads_a_multi_character_identifier(self):
    tokenizer = self.create_tokenizer("abc123_  ")

    return_value = tokenizer.read_identifier()

    self.assertEqual("abc123_", return_value)
    self.assertFalse(tokenizer.eof())
    self.assertTrue(tokenizer.skip_whitespace())
    self.assertTrue(tokenizer.eof())

  def test_read_identifier_reads_a_multi_character_identifier_to_eof(self):
    tokenizer = self.create_tokenizer("abc123_")

    return_value = tokenizer.read_identifier()

    self.assertEqual("abc123_", return_value)
    self.assertTrue(tokenizer.eof())

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

  def test_skip_whitespace_on_empty_file(self):
    tokenizer = self.create_tokenizer("")

    return_value = tokenizer.skip_whitespace()

    self.assertFalse(return_value)
    self.assertTrue(tokenizer.eof())

  def test_skip_whitespace_when_not_on_whitespace(self):
    tokenizer = self.create_tokenizer("abcd")

    return_value = tokenizer.skip_whitespace()

    self.assertFalse(return_value)
    self.assertFalse(tokenizer.eof())

  def test_skip_whitespace_on_entirely_whitespace_file(self):
    tokenizer = self.create_tokenizer("\t\r\n  \n  \r \r\r  \n\n  \t")

    return_value = tokenizer.skip_whitespace()

    self.assertTrue(return_value)
    self.assertTrue(tokenizer.eof())

  def test_skip_whitespace_skips_to_first_non_whitespace_character(self):
    tokenizer = self.create_tokenizer("\r\n \n \n\n\r   \t\t\r\nabc")

    return_value = tokenizer.skip_whitespace()

    self.assertTrue(return_value)
    self.assertFalse(tokenizer.eof())
    self.assertEqual("abc", tokenizer.read_identifier())

  def test_skip_inline_comment_on_empty_file(self):
    tokenizer = self.create_tokenizer("")

    return_value = tokenizer.skip_inline_comment()

    self.assertFalse(return_value)
    tokenizer.skip_whitespace()
    self.assertTrue(tokenizer.eof())

  def test_skip_inline_comment_when_not_at_a_comment(self):
    tokenizer = self.create_tokenizer("abcd")

    return_value = tokenizer.skip_inline_comment()

    self.assertFalse(return_value)
    self.assertFalse(tokenizer.eof())

  def test_skip_inline_comment_on_file_containing_entire_an_inline_comment(self):
    tokenizer = self.create_tokenizer("// This comment is the entire file")

    return_value = tokenizer.skip_inline_comment()

    self.assertTrue(return_value)
    tokenizer.skip_whitespace()
    self.assertTrue(tokenizer.eof())

  def test_skip_inline_comment_skips_embedded_slash_slash(self):
    tokenizer = self.create_tokenizer("// A comment/////////\rabc")

    return_value = tokenizer.skip_inline_comment()

    self.assertTrue(return_value)
    tokenizer.skip_whitespace()
    self.assertEqual("abc", tokenizer.read_identifier())

  def test_skip_inline_comment_skips_entirely_slash_comment(self):
    tokenizer = self.create_tokenizer("///////////\rabc")

    return_value = tokenizer.skip_inline_comment()

    self.assertTrue(return_value)
    tokenizer.skip_whitespace()
    self.assertEqual("abc", tokenizer.read_identifier())

  def test_skip_inline_comment_skips_until_but_excluding_cr(self):
    tokenizer = self.create_tokenizer("// A comment\rabc")

    return_value = tokenizer.skip_inline_comment()

    self.assertTrue(return_value)
    tokenizer.skip_whitespace()
    self.assertEqual("abc", tokenizer.read_identifier())

  def test_skip_inline_comment_skips_until_but_excluding_lf(self):
    tokenizer = self.create_tokenizer("// A comment\nabc")

    return_value = tokenizer.skip_inline_comment()

    self.assertTrue(return_value)
    tokenizer.skip_whitespace()
    self.assertEqual("abc", tokenizer.read_identifier())

  def test_skip_inline_comment_skips_until_but_excluding_crlf(self):
    tokenizer = self.create_tokenizer("// A comment\r\nabc")

    return_value = tokenizer.skip_inline_comment()

    self.assertTrue(return_value)
    tokenizer.skip_whitespace()
    self.assertEqual("abc", tokenizer.read_identifier())

  def test_skip_multiline_comment_on_empty_file(self):
    tokenizer = self.create_tokenizer("/* This comment is the entire file\r\n \n \r \t*/")

    return_value = tokenizer.skip_multiline_comment()

    self.assertTrue(return_value)
    tokenizer.skip_whitespace()
    self.assertTrue(tokenizer.eof())

  def test_skip_multiline_comment_when_not_on_a_comment(self):
    tokenizer = self.create_tokenizer("abcd")

    return_value = tokenizer.skip_multiline_comment()

    self.assertFalse(return_value)
    self.assertFalse(tokenizer.eof())

  def test_skip_multiline_comment_on_file_containing_entirely_a_multiline_comment(self):
    tokenizer = self.create_tokenizer("/* This comment is the entire file\r\n \n \r \t  */")

    return_value = tokenizer.skip_multiline_comment()

    self.assertTrue(return_value)
    tokenizer.skip_whitespace()
    self.assertTrue(tokenizer.eof())

  def test_skip_multiline_comment_on_comment_containing_entirely_stars(self):
    tokenizer = self.create_tokenizer("/************/abc")

    return_value = tokenizer.skip_multiline_comment()

    self.assertTrue(return_value)
    self.assertEqual("abc", tokenizer.read_identifier())

  def test_read_annotation_on_empty_file(self):
    tokenizer = self.create_tokenizer("")

    return_value = tokenizer.read_annotation()

    self.assertIsNone(return_value)

  def test_read_annotation_on_file_containing_only_an_annotation(self):
    tokenizer = self.create_tokenizer("@abc")

    return_value = tokenizer.read_annotation()

    self.assertEqual("abc", return_value)

  def test_read_annotation_when_not_at_an_annotation(self):
    tokenizer = self.create_tokenizer("abc")

    return_value = tokenizer.read_annotation()

    self.assertIsNone(return_value)

  def test_read_annotation_when_file_ends_after_the_at_symbol(self):
    tokenizer = self.create_tokenizer("@")

    with self.assertRaises(tokenizer.ParseError) as assert_raises_context:
      tokenizer.read_annotation()

    exception_message = str(assert_raises_context.exception)
    self.assertIn("expected annotation", exception_message.lower())
    self.assertIn("@", exception_message)

  def test_read_annotation_when_non_identifier_follows_the_at_symbol(self):
    tokenizer = self.create_tokenizer("@123")

    with self.assertRaises(tokenizer.ParseError) as assert_raises_context:
      tokenizer.read_annotation()

    exception_message = str(assert_raises_context.exception)
    self.assertIn("expected annotation", exception_message.lower())
    self.assertIn("@", exception_message)

  def create_tokenizer(self, text: str) -> Tokenizer:
    return Tokenizer(source_reader=source_reader_module.SourceReader(io.StringIO(text)))


if __name__ == "__main__":
  absltest.main()

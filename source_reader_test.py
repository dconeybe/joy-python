import io

from absl.testing import absltest
import parameterized

import source_reader as source_reader_module


SourceReader = source_reader_module.SourceReader
ReadMode = source_reader_module.ReadMode

# TODO: Add tests for lexeme_length()
# TODO: Add tests for max_lexeme_length argument to read()


class SourceReaderTest(absltest.TestCase):

  def test_lexeme_on_new_instance_should_return_empty_string(self):
    source_reader = SourceReader(io.StringIO())
    self.assertEqual("", source_reader.lexeme())

  def test_eof_on_new_instance_should_return_False(self):
    source_reader = SourceReader(io.StringIO())
    self.assertFalse(source_reader.eof())

  @parameterized.parameterized.expand([
      ("NORMAL", ReadMode.NORMAL),
      ("APPEND", ReadMode.APPEND),
      ("SKIP", ReadMode.SKIP),
  ])
  def test_read_on_empty_file_should_immediately_enter_eof_state(self, _, read_mode: ReadMode):
    source_reader = SourceReader(io.StringIO())

    source_reader.read(accepted_characters="", mode=read_mode, max_lexeme_length=100)

    self.assertTrue(source_reader.eof())
    self.assertEqual(source_reader.lexeme(), "")

  @parameterized.parameterized.expand([
      ("NORMAL", ReadMode.NORMAL, "abcdef"),
      ("APPEND", ReadMode.APPEND, "abcdef"),
      ("SKIP", ReadMode.SKIP, ""),
  ])
  def test_read_to_eof_should_enter_and_remain_in_eof_state(
      self, _, read_mode: ReadMode, expected_lexeme: str
  ):
    source_reader = SourceReader(io.StringIO("abcdef"))

    source_reader.read(accepted_characters="abcdef", mode=read_mode, max_lexeme_length=100)
    self.assertTrue(source_reader.eof())
    self.assertEqual(expected_lexeme, source_reader.lexeme())

    source_reader.read(accepted_characters="", mode=read_mode, max_lexeme_length=100)
    self.assertTrue(source_reader.eof())
    self.assertEqual(expected_lexeme, source_reader.lexeme())
    source_reader.read(accepted_characters="", mode=read_mode, max_lexeme_length=100)
    self.assertTrue(source_reader.eof())
    self.assertEqual(expected_lexeme, source_reader.lexeme())

  @parameterized.parameterized.expand([
      ("NORMAL", ReadMode.NORMAL, ("aaa", "bbb", "ccc")),
      ("APPEND", ReadMode.APPEND, ("aaa", "aaabbb", "aaabbbccc")),
      ("SKIP", ReadMode.SKIP, ("", "", "")),
  ])
  def test_read_consecutive_calls(self, _, read_mode: ReadMode, expected_lexemes: tuple[str]):
    source_reader = SourceReader(io.StringIO("aaabbbccc"))

    source_reader.read(accepted_characters="a", mode=read_mode, max_lexeme_length=100)
    self.assertEqual(expected_lexemes[0], source_reader.lexeme())
    self.assertFalse(source_reader.eof())

    source_reader.read(accepted_characters="b", mode=read_mode, max_lexeme_length=100)
    self.assertEqual(expected_lexemes[1], source_reader.lexeme())
    self.assertFalse(source_reader.eof())

    source_reader.read(accepted_characters="c", mode=read_mode, max_lexeme_length=100)
    self.assertEqual(expected_lexemes[2], source_reader.lexeme())
    self.assertTrue(source_reader.eof())

  @parameterized.parameterized.expand([
      ("NORMAL", ReadMode.NORMAL, ("aaabb", "bcccd", "ddeee"), ""),
      ("APPEND", ReadMode.APPEND, ("aaabb", "aaabb", "aaabb"), "bcccdddeee"),
      ("SKIP", ReadMode.SKIP, ("", "", ""), ""),
  ])
  def test_read_should_stop_after_lexeme_length_reaches_max_lexeme_length(
      self, _, read_mode: ReadMode, expected_lexemes: tuple[str], final_lexeme: str
  ):
    source_reader = SourceReader(io.StringIO("aaabbbcccdddeee"))

    source_reader.read(accepted_characters="abcde", mode=read_mode, max_lexeme_length=5)
    self.assertEqual(expected_lexemes[0], source_reader.lexeme())
    self.assertFalse(source_reader.eof())

    source_reader.read(accepted_characters="abcde", mode=read_mode, max_lexeme_length=5)
    self.assertEqual(expected_lexemes[1], source_reader.lexeme())
    self.assertFalse(source_reader.eof())

    source_reader.read(accepted_characters="abcde", mode=read_mode, max_lexeme_length=5)
    self.assertEqual(expected_lexemes[2], source_reader.lexeme())
    self.assertFalse(source_reader.eof())

    source_reader.read(accepted_characters="abcde", mode=ReadMode.NORMAL, max_lexeme_length=100)
    self.assertEqual(final_lexeme, source_reader.lexeme())
    self.assertTrue(source_reader.eof())

  def test_read_when_lexeme_spans_buffer_sizes_basic_test(self):
    source_reader = SourceReader(io.StringIO("aaaXXXcccYYYddd"), buffer_size=5)

    source_reader.read(accepted_characters="abcdXY", mode=ReadMode.NORMAL, max_lexeme_length=100)
    self.assertEqual("aaaXXXcccYYYddd", source_reader.lexeme())
    self.assertTrue(source_reader.eof())

  @parameterized.parameterized.expand([
      ("NORMAL", ReadMode.NORMAL, ("aaaXXXccc", "YYY", "ddd")),
      ("APPEND", ReadMode.APPEND, ("aaaXXXccc", "aaaXXXcccYYY", "aaaXXXcccYYYddd")),
      ("SKIP", ReadMode.SKIP, ("", "", "")),
  ])
  def test_read_when_lexeme_spans_buffer_sizes(
      self, _, read_mode: ReadMode, expected_lexemes: tuple[str]
  ):
    source_reader = SourceReader(io.StringIO("aaaXXXcccYYYddd"), buffer_size=5)

    source_reader.read(accepted_characters="aXc", mode=read_mode, max_lexeme_length=100)
    self.assertEqual(expected_lexemes[0], source_reader.lexeme())
    self.assertFalse(source_reader.eof())

    source_reader.read(accepted_characters="Y", mode=read_mode, max_lexeme_length=100)
    self.assertEqual(expected_lexemes[1], source_reader.lexeme())
    self.assertFalse(source_reader.eof())

    source_reader.read(accepted_characters="d", mode=read_mode, max_lexeme_length=100)
    self.assertEqual(expected_lexemes[2], source_reader.lexeme())
    self.assertTrue(source_reader.eof())

    source_reader.read(accepted_characters="acdXY", mode=read_mode, max_lexeme_length=100)
    self.assertEqual(expected_lexemes[2], source_reader.lexeme())
    self.assertTrue(source_reader.eof())

  def test_read_when_lexeme_spans_buffer_sizes_complex_test(self):
    source_reader = SourceReader(io.StringIO("aaaXXXcccYYY" * 100), buffer_size=3)

    source_reader.read(accepted_characters="aXc", mode=ReadMode.NORMAL, max_lexeme_length=100)
    self.assertEqual("aaaXXXccc", source_reader.lexeme())
    source_reader.read(accepted_characters="YaX", mode=ReadMode.APPEND, max_lexeme_length=100)
    self.assertEqual("aaaXXXcccYYYaaaXXX", source_reader.lexeme())
    source_reader.read(accepted_characters="cYa", mode=ReadMode.APPEND, max_lexeme_length=100)
    self.assertEqual("aaaXXXcccYYYaaaXXXcccYYYaaa", source_reader.lexeme())
    source_reader.read(accepted_characters="Xc", mode=ReadMode.SKIP, max_lexeme_length=100)
    self.assertEqual("", source_reader.lexeme())
    source_reader.read(accepted_characters="YaX", mode=ReadMode.APPEND, max_lexeme_length=100)
    self.assertEqual("YYYaaaXXX", source_reader.lexeme())
    source_reader.read(accepted_characters="cYa", mode=ReadMode.NORMAL, max_lexeme_length=100)
    self.assertEqual("cccYYYaaa", source_reader.lexeme())
    source_reader.read(accepted_characters="acXY", mode=ReadMode.NORMAL, max_lexeme_length=10000)
    self.assertTrue(source_reader.eof())

  @parameterized.parameterized.expand([
      ("NORMAL", ReadMode.NORMAL, ("aaaXXXcc", "cYY", "YaaaXXXcccYYYaaaX")),
      ("APPEND", ReadMode.APPEND, ("aaaXXXcc", "aaaXXXcc", "aaaXXXcccYYYaaaXX")),
      ("SKIP", ReadMode.SKIP, ("", "", "")),
  ])
  def test_read_when_lexeme_spans_buffer_sizes_and_hits_max_length(
      self, _, read_mode: ReadMode, expected_lexemes: tuple[str]
  ):
    source_reader = SourceReader(io.StringIO("aaaXXXcccYYY" * 100), buffer_size=2)

    source_reader.read(accepted_characters="aXc", mode=read_mode, max_lexeme_length=8)
    self.assertEqual(expected_lexemes[0], source_reader.lexeme())
    self.assertFalse(source_reader.eof())

    source_reader.read(accepted_characters="cY", mode=read_mode, max_lexeme_length=3)
    self.assertEqual(expected_lexemes[1], source_reader.lexeme())
    self.assertFalse(source_reader.eof())

    source_reader.read(accepted_characters="cYaX", mode=read_mode, max_lexeme_length=17)
    self.assertEqual(expected_lexemes[2], source_reader.lexeme())


if __name__ == "__main__":
  absltest.main()

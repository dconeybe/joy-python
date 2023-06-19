import dataclasses
import io

from absl.testing import absltest
import parameterized

import source_reader as source_reader_module


SourceReader = source_reader_module.SourceReader
ReadMode = source_reader_module.ReadMode

# TODO: Add tests for lexeme_length()
# TODO: Add tests for max_lexeme_length argument to read()


class SourceReaderTest(absltest.TestCase):

  def test_new_instance_state(self):
    source_reader = SourceReader(io.StringIO())
    self.assertSourceReaderState(source_reader, lexeme="", eof=False)

  @parameterized.parameterized.expand([
      ("NORMAL", ReadMode.NORMAL),
      ("APPEND", ReadMode.APPEND),
      ("SKIP", ReadMode.SKIP),
  ])
  def test_read_on_empty_file_should_immediately_enter_eof_state(self, _, read_mode: ReadMode):
    source_reader = SourceReader(io.StringIO())

    source_reader.read(accepted_characters="", mode=read_mode, max_lexeme_length=100)

    self.assertSourceReaderState(source_reader, lexeme="", eof=True)

  @parameterized.parameterized.expand([
      ("NORMAL", ReadMode.NORMAL, "abcdef", ""),
      ("APPEND", ReadMode.APPEND, "abcdef", "abcdef"),
      ("SKIP", ReadMode.SKIP, "", ""),
  ])
  def test_read_to_eof_should_enter_and_remain_in_eof_state(
      self, _, read_mode: ReadMode, expected_lexeme1: str, expected_lexeme2: str
  ):
    source_reader = SourceReader(io.StringIO("abcdef"))

    source_reader.read(accepted_characters="abcdef", mode=read_mode, max_lexeme_length=100)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexeme1, eof=True)

    source_reader.read(accepted_characters="", mode=read_mode, max_lexeme_length=100)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexeme2, eof=True)
    source_reader.read(accepted_characters="", mode=read_mode, max_lexeme_length=100)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexeme2, eof=True)

  @parameterized.parameterized.expand([
      ("NORMAL", ReadMode.NORMAL, ("aaa", "bbb", "ccc")),
      ("APPEND", ReadMode.APPEND, ("aaa", "aaabbb", "aaabbbccc")),
      ("SKIP", ReadMode.SKIP, ("", "", "")),
  ])
  def test_read_consecutive_calls(self, _, read_mode: ReadMode, expected_lexemes: tuple[str]):
    source_reader = SourceReader(io.StringIO("aaabbbccc"))

    source_reader.read(accepted_characters="a", mode=read_mode, max_lexeme_length=100)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[0], eof=False)

    source_reader.read(accepted_characters="b", mode=read_mode, max_lexeme_length=100)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[1], eof=False)

    source_reader.read(accepted_characters="c", mode=read_mode, max_lexeme_length=100)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[2], eof=True)

  @parameterized.parameterized.expand([
      ("NORMAL", ReadMode.NORMAL, ("aaabb", "bcccd", "ddeee", "")),
      ("APPEND", ReadMode.APPEND, ("aaabb", "aaabb", "aaabb", "bcccdddeee")),
      ("SKIP", ReadMode.SKIP, ("", "", "", "")),
  ])
  def test_read_should_stop_after_lexeme_length_reaches_max_lexeme_length(
      self, _, read_mode: ReadMode, expected_lexemes: tuple[str]
  ):
    source_reader = SourceReader(io.StringIO("aaabbbcccdddeee"))

    source_reader.read(accepted_characters="abcde", mode=read_mode, max_lexeme_length=5)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[0], eof=False)

    source_reader.read(accepted_characters="abcde", mode=read_mode, max_lexeme_length=5)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[1], eof=False)

    source_reader.read(accepted_characters="abcde", mode=read_mode, max_lexeme_length=5)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[2], eof=False)

    source_reader.read(accepted_characters="abcde", mode=ReadMode.NORMAL, max_lexeme_length=100)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[3], eof=True)

  def test_read_when_lexeme_spans_buffer_sizes_basic_test(self):
    source_reader = SourceReader(io.StringIO("aaaXXXcccYYYddd"), buffer_size=5)

    source_reader.read(accepted_characters="abcdXY", mode=ReadMode.NORMAL, max_lexeme_length=100)
    self.assertSourceReaderState(source_reader, lexeme="aaaXXXcccYYYddd", eof=True)

  @parameterized.parameterized.expand([
      ("NORMAL", ReadMode.NORMAL, ("aaaXXXccc", "YYY", "ddd", "")),
      (
          "APPEND",
          ReadMode.APPEND,
          ("aaaXXXccc", "aaaXXXcccYYY", "aaaXXXcccYYYddd", "aaaXXXcccYYYddd"),
      ),
      ("SKIP", ReadMode.SKIP, ("", "", "", "")),
  ])
  def test_read_when_lexeme_spans_buffer_sizes(
      self, _, read_mode: ReadMode, expected_lexemes: tuple[str]
  ):
    source_reader = SourceReader(io.StringIO("aaaXXXcccYYYddd"), buffer_size=5)

    source_reader.read(accepted_characters="aXc", mode=read_mode, max_lexeme_length=100)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[0], eof=False)

    source_reader.read(accepted_characters="Y", mode=read_mode, max_lexeme_length=100)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[1], eof=False)

    source_reader.read(accepted_characters="d", mode=read_mode, max_lexeme_length=100)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[2], eof=True)

    source_reader.read(accepted_characters="acdXY", mode=read_mode, max_lexeme_length=100)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[3], eof=True)

  def test_read_when_lexeme_spans_buffer_sizes_complex_test(self):
    source_reader = SourceReader(io.StringIO("aaaXXXcccYYY" * 100), buffer_size=3)

    source_reader.read(accepted_characters="aXc", mode=ReadMode.NORMAL, max_lexeme_length=100)
    self.assertSourceReaderState(source_reader, lexeme="aaaXXXccc", eof=False)
    source_reader.read(accepted_characters="YaX", mode=ReadMode.APPEND, max_lexeme_length=100)
    self.assertSourceReaderState(source_reader, lexeme="aaaXXXcccYYYaaaXXX", eof=False)
    source_reader.read(accepted_characters="cYa", mode=ReadMode.APPEND, max_lexeme_length=100)
    self.assertSourceReaderState(source_reader, lexeme="aaaXXXcccYYYaaaXXXcccYYYaaa", eof=False)
    source_reader.read(accepted_characters="Xc", mode=ReadMode.SKIP, max_lexeme_length=100)
    self.assertSourceReaderState(source_reader, lexeme="", eof=False)
    source_reader.read(accepted_characters="YaX", mode=ReadMode.APPEND, max_lexeme_length=100)
    self.assertSourceReaderState(source_reader, lexeme="YYYaaaXXX", eof=False)
    source_reader.read(accepted_characters="cYa", mode=ReadMode.NORMAL, max_lexeme_length=100)
    self.assertSourceReaderState(source_reader, lexeme="cccYYYaaa", eof=False)
    source_reader.read(accepted_characters="acXY", mode=ReadMode.SKIP, max_lexeme_length=10000)
    self.assertSourceReaderState(source_reader, lexeme="", eof=True)

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
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[0], eof=False)

    source_reader.read(accepted_characters="cY", mode=read_mode, max_lexeme_length=3)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[1], eof=False)

    source_reader.read(accepted_characters="cYaX", mode=read_mode, max_lexeme_length=17)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[2], eof=False)

  @parameterized.parameterized.expand([
      ("NORMAL", ReadMode.NORMAL, ("aaa", "XXXbbb", "YYYccc")),
      ("APPEND", ReadMode.APPEND, ("aaa", "aaaXXXbbb", "aaaXXXbbbYYYccc")),
      ("SKIP", ReadMode.SKIP, ("", "", "")),
  ])
  def test_invert_accepted_characters(self, _, read_mode: ReadMode, expected_lexemes: tuple[str]):
    source_reader = SourceReader(io.StringIO("aaaXXXbbbYYYcccZZZ"))

    source_reader.read(
        accepted_characters="X",
        mode=read_mode,
        max_lexeme_length=100,
        invert_accepted_characters=True,
    )
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[0], eof=False)

    source_reader.read(
        accepted_characters="Y",
        mode=read_mode,
        max_lexeme_length=100,
        invert_accepted_characters=True,
    )
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[1], eof=False)

    source_reader.read(
        accepted_characters="Z",
        mode=read_mode,
        max_lexeme_length=100,
        invert_accepted_characters=True,
    )
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[2], eof=False)

  @parameterized.parameterized.expand([
      ("NORMAL", ReadMode.NORMAL),
      ("APPEND", ReadMode.APPEND),
      ("SKIP", ReadMode.SKIP),
  ])
  def test_read_until_exact_match_with_empty_text_should_raise(self, _, read_mode: ReadMode):
    source_reader = SourceReader(io.StringIO("abc"))

    with self.assertRaises(ValueError) as assert_raises_context:
      source_reader.read_until_exact_match("", read_mode)

    exception_message = str(assert_raises_context.exception)
    self.assertIn("empty string", exception_message.lower())

  @parameterized.parameterized.expand([
      ("NORMAL", ReadMode.NORMAL),
      ("APPEND", ReadMode.APPEND),
      ("SKIP", ReadMode.SKIP),
  ])
  def test_read_until_exact_match_on_empty_input(self, _, read_mode: ReadMode):
    source_reader = SourceReader(io.StringIO(), buffer_size=3)

    return_value = source_reader.read_until_exact_match("abc", read_mode)

    self.assertFalse(return_value)
    self.assertSourceReaderState(source_reader, lexeme="", eof=True)

  @parameterized.parameterized.expand([
      ("NORMAL", ReadMode.NORMAL, "aaabCzza  bc\nbca\r\n\t"),
      ("APPEND", ReadMode.APPEND, "aaabCzza  bc\nbca\r\n\t"),
      ("SKIP", ReadMode.SKIP, ""),
  ])
  def test_read_until_exact_match_with_no_match_should_read_to_eof(
      self, _, read_mode: ReadMode, expected_lexeme: str
  ):
    source_reader = SourceReader(io.StringIO("aaabCzza  bc\nbca\r\n\t"), buffer_size=3)

    return_value = source_reader.read_until_exact_match("abc", read_mode)

    self.assertFalse(return_value)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexeme, eof=True)

  @parameterized.parameterized.expand([
      ("NORMAL", ReadMode.NORMAL, ["aaa bbb", " ccc ddd eee f", "ff ggg", ""]),
      (
          "APPEND",
          ReadMode.APPEND,
          [
              "aaa bbb",
              "aaa bbb ccc ddd eee f",
              "aaa bbb ccc ddd eee fff ggg",
              "aaa bbb ccc ddd eee fff ggg",
          ],
      ),
      ("SKIP", ReadMode.SKIP, ["", "", "", ""]),
  ])
  def test_read_until_exact_match_with_match_in_the_middle(
      self, _, read_mode: ReadMode, expected_lexemes: list[str]
  ):
    source_reader = SourceReader(io.StringIO("aaa bbb ccc ddd eee fff ggg"), buffer_size=3)

    return_value1 = source_reader.read_until_exact_match("bbb", read_mode)
    self.assertTrue(return_value1)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[0], eof=False)

    return_value2 = source_reader.read_until_exact_match("e f", read_mode)
    self.assertTrue(return_value2)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[1], eof=False)

    return_value3 = source_reader.read_until_exact_match("ggg", read_mode)
    self.assertTrue(return_value3)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[2], eof=False)

    return_value4 = source_reader.read_until_exact_match("zzz", read_mode)
    self.assertFalse(return_value4)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexemes[3], eof=True)

  @parameterized.parameterized.expand([
      ("NORMAL", ReadMode.NORMAL, "abcdefg"),
      ("APPEND", ReadMode.APPEND, "abcdefg"),
      ("SKIP", ReadMode.SKIP, ""),
  ])
  def test_peek_on_new_instance(self, _, read_mode: ReadMode, expected_lexeme: str):
    source_reader = SourceReader(io.StringIO("abcdefg"), buffer_size=3)

    return_value = source_reader.peek(7)

    self.assertEqual("abcdefg", return_value)
    self.assertSourceReaderState(source_reader, lexeme="", eof=False)
    source_reader.read(accepted_characters="abcdefg", mode=read_mode, max_lexeme_length=100)
    self.assertSourceReaderState(source_reader, lexeme=expected_lexeme, eof=True)

  @parameterized.parameterized.expand([
      ("NORMAL", ReadMode.NORMAL, "bcdefghijklmnopqrstuvwxyz"),
      ("APPEND", ReadMode.APPEND, "abcdefghijklmnopqrstuvwxyz"),
      ("SKIP", ReadMode.SKIP, ""),
  ])
  def test_peek_when_buffer_is_full(self, _, read_mode: ReadMode, expected_lexeme: str):
    source_reader = SourceReader(io.StringIO("abcdefghijklmnopqrstuvwxyz"), buffer_size=100)
    source_reader.read(accepted_characters="a", mode=read_mode, max_lexeme_length=1)

    return_value = source_reader.peek(10)

    self.assertEqual("bcdefghijk", return_value)
    source_reader.read(
        accepted_characters="",
        mode=read_mode,
        max_lexeme_length=100,
        invert_accepted_characters=True,
    )
    self.assertSourceReaderState(source_reader, lexeme=expected_lexeme, eof=True)

  @parameterized.parameterized.expand([
      ("NORMAL", ReadMode.NORMAL, "abcdefghijklmnopqrstuvwxyz"),
      ("APPEND", ReadMode.APPEND, "abcdefghijklmnopqrstuvwxyz"),
      ("SKIP", ReadMode.SKIP, ""),
  ])
  def test_peek_when_result_spans_buffers(self, _, read_mode: ReadMode, expected_lexeme: str):
    source_reader = SourceReader(io.StringIO("abcdefghijklmnopqrstuvwxyz"), buffer_size=3)

    return_value = source_reader.peek(10)

    self.assertEqual("abcdefghij", return_value)
    source_reader.read(
        accepted_characters="",
        mode=read_mode,
        max_lexeme_length=100,
        invert_accepted_characters=True,
    )
    self.assertSourceReaderState(source_reader, lexeme=expected_lexeme, eof=True)

  @parameterized.parameterized.expand([
      ("NORMAL", ReadMode.NORMAL, "abcdefghijklmnopqrstuvwxyz"),
      ("APPEND", ReadMode.APPEND, "abcdefghijklmnopqrstuvwxyz"),
      ("SKIP", ReadMode.SKIP, ""),
  ])
  def test_peek_when_at_eof(self, _, read_mode: ReadMode, expected_lexeme: str):
    source_reader = SourceReader(io.StringIO("aaaa"), buffer_size=3)
    source_reader.read(accepted_characters="a", mode=ReadMode.SKIP, max_lexeme_length=100)
    self.assertSourceReaderState(source_reader, lexeme="", eof=True)

    return_value = source_reader.peek(10)

    self.assertEqual("", return_value)

  def assertSourceReaderState(self, source_reader: SourceReader, lexeme: str, eof: bool) -> None:
    actual_state = SourceReaderState(
        lexeme=source_reader.lexeme(),
        lexeme_length=source_reader.lexeme_length(),
        eof=source_reader.eof(),
    )
    expected_state = SourceReaderState(
        lexeme=lexeme,
        lexeme_length=len(lexeme),
        eof=eof,
    )

    differing_properties: list[str] = []
    if actual_state.lexeme != expected_state.lexeme:
      differing_properties.append("lexeme")
    if actual_state.lexeme_length != expected_state.lexeme_length:
      differing_properties.append("lexeme_length")
    if actual_state.eof != expected_state.eof:
      differing_properties.append("eof")

    self.assertEqual(
        expected_state, actual_state, msg=f"differing properties: {', '.join(differing_properties)}"
    )


@dataclasses.dataclass(frozen=True)
class SourceReaderState:
  lexeme: str
  lexeme_length: int
  eof: bool


if __name__ == "__main__":
  absltest.main()

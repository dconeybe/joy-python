import io

from absl.testing import absltest

import source_reader as source_reader_module


SourceReader = source_reader_module.SourceReader
ReadMode = source_reader_module.ReadMode


class SourceReaderTest(absltest.TestCase):

  def test_lexeme_on_new_instance_should_return_empty_string(self):
    source_reader = SourceReader(io.StringIO())
    self.assertEqual("", source_reader.lexeme())

  def test_read_on_empty_file_should_immediately_enter_eof_state(self):
    source_reader = SourceReader(io.StringIO())

    source_reader.read(accepted_characters="abc", mode=ReadMode.NORMAL, max_lexeme_length=100)

    self.assertEofState(source_reader)

  def test_read_to_eof_should_enter_and_remain_in_eof_state_upon_subsequent_read_invocations(self):
    source_reader = SourceReader(io.StringIO("abcdef"))

    source_reader.read(accepted_characters="abcdef", mode=ReadMode.NORMAL, max_lexeme_length=100)
    self.assertFalse(source_reader.eof())
    self.assertEqual("abcdef", source_reader.lexeme())

    for i in range(10):
      with self.subTest(i=i):
        source_reader.read(
            accepted_characters="abcdef", mode=ReadMode.NORMAL, max_lexeme_length=100
        )
        self.assertEofState(source_reader)

  def test_read_normal_mode_replaces_the_lexeme_between_calls(self):
    source_reader = SourceReader(io.StringIO("aaabbbccc"))

    source_reader.read(accepted_characters="a", mode=ReadMode.NORMAL, max_lexeme_length=100)
    self.assertEqual("aaa", source_reader.lexeme())

    source_reader.read(accepted_characters="b", mode=ReadMode.NORMAL, max_lexeme_length=100)
    self.assertEqual("bbb", source_reader.lexeme())

    source_reader.read(accepted_characters="c", mode=ReadMode.NORMAL, max_lexeme_length=100)
    self.assertEqual("ccc", source_reader.lexeme())

    source_reader.read(accepted_characters="x", mode=ReadMode.NORMAL, max_lexeme_length=100)
    self.assertEofState(source_reader)

  def test_read_append_mode_appends_to_the_lexeme_between_calls(self):
    source_reader = SourceReader(io.StringIO("aaabbbccc"))

    source_reader.read(accepted_characters="a", mode=ReadMode.APPEND, max_lexeme_length=100)
    self.assertEqual("aaa", source_reader.lexeme())

    source_reader.read(accepted_characters="b", mode=ReadMode.APPEND, max_lexeme_length=100)
    self.assertEqual("aaabbb", source_reader.lexeme())

    source_reader.read(accepted_characters="c", mode=ReadMode.APPEND, max_lexeme_length=100)
    self.assertEqual("aaabbbccc", source_reader.lexeme())

    source_reader.read(accepted_characters="x", mode=ReadMode.APPEND, max_lexeme_length=100)
    self.assertEofState(source_reader)

  def test_read_skip_mode_drops_accepted_characters(self):
    source_reader = SourceReader(io.StringIO("aaabbbcccdddeee"))

    source_reader.read(accepted_characters="a", mode=ReadMode.NORMAL, max_lexeme_length=100)
    self.assertEqual("aaa", source_reader.lexeme())

    source_reader.read(accepted_characters="b", mode=ReadMode.SKIP, max_lexeme_length=100)
    self.assertEqual("", source_reader.lexeme())

    source_reader.read(accepted_characters="c", mode=ReadMode.SKIP, max_lexeme_length=100)
    self.assertEqual("", source_reader.lexeme())

    source_reader.read(accepted_characters="d", mode=ReadMode.APPEND, max_lexeme_length=100)
    self.assertEqual("ddd", source_reader.lexeme())

    source_reader.read(accepted_characters="e", mode=ReadMode.SKIP, max_lexeme_length=100)
    self.assertEqual("", source_reader.lexeme())

    source_reader.read(accepted_characters="x", mode=ReadMode.SKIP, max_lexeme_length=100)
    self.assertEqual("", source_reader.lexeme())

    self.assertEofState(source_reader)

  def assertEofState(self, source_reader: SourceReader) -> None:
    with self.subTest("eof"):
      self.assertTrue(source_reader.eof())
    with self.subTest("lexeme"):
      self.assertEqual("", source_reader.lexeme())


if __name__ == "__main__":
  absltest.main()

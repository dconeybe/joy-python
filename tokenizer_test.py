import io

from absl.testing import absltest

import tokenizer


class SourceReaderTest(absltest.TestCase):

  def test_empty_file_should_produce_no_characters(self):
    source_reader = tokenizer.SourceReader(io.StringIO())

    read_result = source_reader.read()

    self.assertIsNone(read_result)

  def test_should_produce_one_character_for_each_character_in_the_file(self):
    source_reader = tokenizer.SourceReader(io.StringIO("abc \r\n 123 _$"))

    read_results = self.read_all(source_reader)

    self.assertLen(read_results, 13)

  def test_should_produce_the_correct_characters(self):
    source_reader = tokenizer.SourceReader(io.StringIO("abc \r\n 123 _$"))

    read_results = self.read_all(source_reader)

    read_chars = "".join(read_result.c for read_result in read_results)
    self.assertEqual(read_chars, "abc \r\n 123 _$")

  def test_should_produce_the_correct_line_numbers(self):
    source_reader = tokenizer.SourceReader(io.StringIO("A \r\n Z\n\n_ \r$"))

    read_results = self.read_all(source_reader)

    read_line_numbers = tuple(read_result.line_number for read_result in read_results)
    self.assertEqual(read_line_numbers, (1, 1, 1, 1, 2, 2, 2, 3, 4, 4, 4, 5))

  def test_should_produce_the_correct_column_numbers(self):
    source_reader = tokenizer.SourceReader(io.StringIO("abc \r\n def\n\n_ \r$"))

    read_results = self.read_all(source_reader)

    read_column_numbers = tuple(read_result.column_number for read_result in read_results)
    self.assertEqual(read_column_numbers, (1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 1, 1, 2, 3, 1))

  def test_skip_chars_should_be_skipped(self):
    source_reader = tokenizer.SourceReader(io.StringIO("abcdefgabcdefgabcdefg"))

    read_results = self.read_all(source_reader, skip_chars="aceg")

    read_chars = "".join(read_result.c for read_result in read_results)
    self.assertEqual(read_chars, "bdfbdfbdf")

  def test_skip_chars_should_still_produce_correct_line_numbers(self):
    source_reader = tokenizer.SourceReader(io.StringIO("abcdefg\nabcdefg\r\nabcdefg"))

    read_results = self.read_all(source_reader, skip_chars="aceg")

    read_line_numbers = tuple(read_result.line_number for read_result in read_results)
    self.assertEqual(read_line_numbers, (1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3))

  def test_skip_chars_should_still_produce_correct_column_numbers(self):
    source_reader = tokenizer.SourceReader(io.StringIO("abcdefg\nabcdefg\r\nabcdefg"))

    read_results = self.read_all(source_reader, skip_chars="aceg")

    read_column_numbers = tuple(read_result.column_number for read_result in read_results)
    self.assertEqual(read_column_numbers, (2, 4, 6, 8, 2, 4, 6, 8, 9, 2, 4, 6))

  def test_skip_chars_should_still_produce_correct_line_numbers_when_skipping_whitespace(self):
    source_reader = tokenizer.SourceReader(io.StringIO("abc\ndef\n\nghi\r\n\rj"))

    read_results = self.read_all(source_reader, skip_chars="\r\n")

    read_line_numbers = tuple(read_result.line_number for read_result in read_results)
    self.assertEqual(read_line_numbers, (1, 1, 1, 2, 2, 2, 4, 4, 4, 6))

  def test_skip_chars_should_still_produce_correct_column_numbers_when_skipping_whitespace(self):
    source_reader = tokenizer.SourceReader(io.StringIO("abc\ndef\n\nghi\r\n\rj"))

    read_results = self.read_all(source_reader, skip_chars="\r\n")

    read_column_numbers = tuple(read_result.column_number for read_result in read_results)
    self.assertEqual(read_column_numbers, (1, 2, 3, 1, 2, 3, 1, 2, 3, 1))

  def test_unread_should_cause_read_to_return_the_exact_same_token(self):
    source_reader = tokenizer.SourceReader(io.StringIO("abc"))

    token1 = source_reader.read()
    source_reader.unread()
    self.assertIs(source_reader.read(), token1)

    token2 = source_reader.read()
    source_reader.unread()
    self.assertIs(source_reader.read(), token2)

    token3 = source_reader.read()
    source_reader.unread()
    self.assertIs(source_reader.read(), token3)

  def test_unread_should_do_nothing_if_invoked_after_end_of_file(self):
    source_reader = tokenizer.SourceReader(io.StringIO("abc"))
    source_reader.read()
    source_reader.read()
    source_reader.read()
    last_token = source_reader.read()
    self.assertIsNone(last_token)  # Make sure we are actually at the end-of-file

    source_reader.unread()

    self.assertIsNone(source_reader.read())

  def test_unread_should_raise_if_invoked_before_read(self):
    source_reader = tokenizer.SourceReader(io.StringIO("abc"))

    with self.assertRaises(RuntimeError) as assert_raises_context:
      source_reader.unread()

    exception_message = str(assert_raises_context.exception).lower()
    self.assertRegex(exception_message, r"read().*invoked.*once")

  def test_unread_should_raise_if_invoked_multiple_times_without_interleaving_read_invocation(self):
    source_reader = tokenizer.SourceReader(io.StringIO("abc"))
    source_reader.read()
    source_reader.unread()

    with self.assertRaises(RuntimeError) as assert_raises_context:
      source_reader.unread()

    exception_message = str(assert_raises_context.exception).lower()
    self.assertRegex(exception_message, r"invoked multiple times")

  def read_all(
      self, source_reader: tokenizer.SourceReader, max_num_chars: int | None = None, **kwargs
  ) -> list[tokenizer.SourceCharacter]:
    read_results = []
    for _ in range(max_num_chars if max_num_chars is not None else 1000):
      read_result = source_reader.read(**kwargs)
      if read_result is None:
        break
      read_results.append(read_result)
    else:
      self.fail(f"SourceReader maximum number of results returned: {len(read_results)}")

    return read_results


class TokenizerTest(absltest.TestCase):

  def test_empty_file_should_produce_no_tokens(self):
    t = tokenizer.Tokenizer(tokenizer.SourceReader(io.StringIO()))

    token = t.next()

    self.assertIsNone(token)

  def test_whitespace_file_should_produce_no_tokens(self):
    t = tokenizer.Tokenizer(tokenizer.SourceReader(io.StringIO("  \t\n\r\r\n  \t  \r\n")))

    token = t.next()

    self.assertIsNone(token)

  def test_stream_of_identifier_chars_should_produce_1_token(self):
    source_text = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    t = tokenizer.Tokenizer(tokenizer.SourceReader(io.StringIO(source_text)))

    token = t.next()

    self.assertEqual(
        token,
        tokenizer.Token(
            start_line_number=1,
            end_line_number=1,
            start_column_number=1,
            end_column_number=63,
            identifier=source_text,
        ),
    )

  def test_yields_a_bunch_of_tokens_on_one_line(self):
    source_text = "abc d12 _yz"
    t = tokenizer.Tokenizer(tokenizer.SourceReader(io.StringIO(source_text)))

    token1 = t.next()
    token2 = t.next()
    token3 = t.next()
    token_last = t.next()

    self.assertEqual(
        token1,
        tokenizer.Token(
            start_line_number=1,
            end_line_number=1,
            start_column_number=1,
            end_column_number=3,
            identifier="abc",
        ),
    )
    self.assertEqual(
        token2,
        tokenizer.Token(
            start_line_number=1,
            end_line_number=1,
            start_column_number=5,
            end_column_number=7,
            identifier="d12",
        ),
    )
    self.assertEqual(
        token3,
        tokenizer.Token(
            start_line_number=1,
            end_line_number=1,
            start_column_number=9,
            end_column_number=11,
            identifier="_yz",
        ),
    )
    self.assertIsNone(token_last)


if __name__ == "__main__":
  absltest.main()

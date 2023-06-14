import io

from absl.testing import absltest

import tokenizer


class TokenizerTest(absltest.TestCase):

  def test_empty_file_should_produce_no_tokens(self):
    t = tokenizer.Tokenizer(tokenizer.SourceReader(io.StringIO()))

    token = t.next()

    self.assertIsNone(token)

  def test_whitespace_file_should_produce_no_tokens(self):
    source_text = "\r\n    \t\t\n\r"
    t = tokenizer.Tokenizer(tokenizer.SourceReader(io.StringIO(source_text)))
    token = tokenizer.Token()

    token = t.next()

    self.assertIsNone(token)

  def test_stream_of_identifier_chars_should_produce_1_token(self):
    source_text = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    t = tokenizer.Tokenizer(tokenizer.SourceReader(io.StringIO(source_text)))
    token = tokenizer.Token()

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
    source_text = "abc def ghi a12 b23 a_      b"
    t = tokenizer.Tokenizer(tokenizer.SourceReader(io.StringIO(source_text)))
    token = tokenizer.Token()

    token1 = t.next()
    token2 = t.next()
    token3 = t.next()
    token4 = t.next()
    token5 = t.next()
    token6 = t.next()
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
            identifier="def",
        ),
    )
    self.assertEqual(
        token3,
        tokenizer.Token(
            start_line_number=1,
            end_line_number=1,
            start_column_number=9,
            end_column_number=11,
            identifier="ghi",
        ),
    )
    self.assertEqual(
        token3,
        tokenizer.Token(
            start_line_number=1,
            end_line_number=1,
            start_column_number=13,
            end_column_number=15,
            identifier="a12",
        ),
    )


if __name__ == "__main__":
  absltest.main()

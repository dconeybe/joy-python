import io

import tokenizer

from absl.testing import absltest


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


if __name__ == "__main__":
  absltest.main()

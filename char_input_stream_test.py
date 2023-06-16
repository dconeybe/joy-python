import io

from absl.testing import absltest

import char_input_stream as char_input_stream_module


CharInputStream = char_input_stream_module.CharInputStream


class CharInputStreamTest(absltest.TestCase):

  def test_init_with_default_arguments_sets_attributes_correctly(self):
    f = io.StringIO()

    char_input_stream = CharInputStream(f)

    self.assertIs(f, char_input_stream.f)
    self.assertIsNone(char_input_stream.buffer_size)

  def test_init_with_no_default_arguments_sets_attributes_correctly(self):
    f = io.StringIO()
    buffer_size = 424242424242

    char_input_stream = CharInputStream(f, buffer_size)

    self.assertIs(f, char_input_stream.f)
    self.assertIs(buffer_size, char_input_stream.buffer_size)

  def test_read_that_spans_multiple_buffers(self):
    f = io.StringIO("abcdefghijklmnopqrstuvwxyz")
    char_input_stream = CharInputStream(f, buffer_size=3)

    read_characters = [char_input_stream.read() for _ in range(30)]

    expected_read_characters = list("abcdefghijklmnopqrstuvwxyz")
    expected_read_characters.extend([None] * 4)
    self.assertEqual(expected_read_characters, read_characters)

  def test_mark_before_first_read(self):
    f = io.StringIO("abcdefghijklmnopqrstuvwxyz")
    char_input_stream = CharInputStream(f, buffer_size=3)

    char_input_stream.mark()
    self.assertCharInputStreamReads(char_input_stream, "abcdefghi", eof=False)
    char_input_stream.reset()
    self.assertCharInputStreamReads(char_input_stream, "abcdefghijklmnopqrstuvwxyz")

  def test_mark_at_eof(self):
    f = io.StringIO("abcdefghijklmnopqrstuvwxyz")
    char_input_stream = CharInputStream(f, buffer_size=3)
    self.assertCharInputStreamReads(char_input_stream, "abcdefghijklmnopqrstuvwxyz", eof=False)

    char_input_stream.mark()
    char_input_stream.reset()
    self.assertCharInputStreamReads(char_input_stream, "", eof=True)

  def test_mark_mid_stream(self):
    f = io.StringIO("abcdefghijklmnopqrstuvwxyz")
    char_input_stream = CharInputStream(f, buffer_size=3)

    self.assertCharInputStreamReads(char_input_stream, "abcdefgh", eof=False)
    char_input_stream.mark()
    self.assertCharInputStreamReads(char_input_stream, "ijklmnopqrs", eof=False)
    char_input_stream.reset()
    self.assertCharInputStreamReads(char_input_stream, "ijklmnopqrstuvwxyz", eof=True)

  def test_mark_while_reading_from_a_previous_mark(self):
    f = io.StringIO("abcdefghijklmnopqrstuvwxyz")
    char_input_stream = CharInputStream(f, buffer_size=3)

    self.assertCharInputStreamReads(char_input_stream, "abcdefghi", eof=False)
    char_input_stream.mark()
    self.assertCharInputStreamReads(char_input_stream, "jklmnopqrst", eof=False)
    char_input_stream.reset()
    self.assertCharInputStreamReads(char_input_stream, "jklmno", eof=False)
    char_input_stream.mark()
    self.assertCharInputStreamReads(char_input_stream, "pqrstuvwx", eof=False)
    char_input_stream.reset()
    self.assertCharInputStreamReads(char_input_stream, "pqrstuvwxyz", eof=True)

  def test_reset_on_a_new_object_should_raise(self):
    f = io.StringIO("abcdefghijklmnopqrstuvwxyz")
    char_input_stream = CharInputStream(f, buffer_size=3)

    with self.assertRaises(RuntimeError) as assert_raises_context:
      char_input_stream.reset()

    exception_message = str(assert_raises_context.exception)
    self.assertIn("reset()", exception_message)
    self.assertIn("mark set", exception_message.lower())

  def test_reset_when_the_mark_has_already_been_deleted_by_a_previous_call_to_reset(self):
    f = io.StringIO("abcdefghijklmnopqrstuvwxyz")
    char_input_stream = CharInputStream(f, buffer_size=3)
    self.assertCharInputStreamReads(char_input_stream, "abcdefgh", eof=False)
    char_input_stream.mark()
    self.assertCharInputStreamReads(char_input_stream, "ijklmnopqr", eof=False)
    char_input_stream.reset()

    with self.assertRaises(RuntimeError) as assert_raises_context:
      char_input_stream.reset()

    exception_message = str(assert_raises_context.exception)
    self.assertIn("reset()", exception_message)
    self.assertIn("mark set", exception_message.lower())

  def test_reset_raises_after_unmark(self):
    f = io.StringIO("abcdefghijklmnopqrstuvwxyz")
    char_input_stream = CharInputStream(f, buffer_size=3)
    self.assertCharInputStreamReads(char_input_stream, "abcdefgh", eof=False)
    char_input_stream.mark()
    char_input_stream.unmark()

    with self.assertRaises(RuntimeError) as assert_raises_context:
      char_input_stream.reset()

    exception_message = str(assert_raises_context.exception)
    self.assertIn("reset()", exception_message)
    self.assertIn("mark set", exception_message.lower())

  def test_unmark_on_new_instance_does_nothing(self):
    f = io.StringIO("abcdefghijklmnopqrstuvwxyz")
    char_input_stream = CharInputStream(f, buffer_size=3)

    char_input_stream.unmark()
    char_input_stream.unmark()
    char_input_stream.unmark()

    self.assertCharInputStreamReads(char_input_stream, "abcdefghijklmnopqrstuvwxyz", eof=False)

  def assertCharInputStreamReads(
      self, char_input_stream: CharInputStream, expected: str, eof: bool = True
  ) -> None:
    read_results = [char_input_stream.read() for _ in range(len(expected))]
    expected_read_results = list(expected)

    if eof:
      read_results.extend(char_input_stream.read() for _ in range(5))
      expected_read_results.extend([None] * 5)

    self.assertEqual(expected_read_results, read_results)


if __name__ == "__main__":
  absltest.main()

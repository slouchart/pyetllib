from unittest import TestCase
from unittest import main as run_tests

import io
from src.pyetllib.etllib.streams import publish_to_stream


class TestPublishToStream(TestCase):
    def setUp(self) -> None:
        self.iterators = (iter(['foo']), iter(['bar']))
        self.stream = io.StringIO()
        self.ctx = {
            'stream': self.stream,
        }

    def test_publish_to_stream_default(self):
        publish_to_stream(*self.iterators, **self.ctx)
        s = self.stream.getvalue()
        self.assertEqual(s, 'foo\nbar\n')

    def test_publish_to_stream_record_delimiter(self):
        self.ctx['record_delimiter'] = '_'
        publish_to_stream(*self.iterators, **self.ctx)
        s = self.stream.getvalue()
        self.assertEqual(s, 'foo_bar_')

    def test_publish_to_stream_record_converter(self):
        self.ctx['record_converter'] = lambda s: str(len(s))
        publish_to_stream(*self.iterators, **self.ctx)
        s = self.stream.getvalue()
        self.assertEqual(s, '3\n3\n')

    def test_all_together(self):
        publish_to_stream(*self.iterators, **self.ctx, record_delimiter='_',
                          record_converter=lambda s: str(len(s)))
        s = self.stream.getvalue()
        self.assertEqual(s, '3_3_')

    def tearDown(self) -> None:
        self.stream.close()


if __name__ == '__main__':
    run_tests(verbosity=2)

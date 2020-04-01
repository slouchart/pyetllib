from unittest import TestCase, main as run_tests

from itertools import count, islice
from functools import partial

from src.pyetllib.etllib import stream_generator, call_next, call_next_starred


class TestStreamGenerator(TestCase):
    def setUp(self) -> None:
        self.make_id = partial(call_next, count(start=1))
        self.make_name = call_next_starred
        self.make_value = call_next_starred

    def test_1(self):
        gen = stream_generator(
            ('id', 'name', 'value', 'constant'),
            (
                self.make_id(),
                self.make_name('foo', 'bar'),
                self.make_value(0.5, 0.7),
                42
            ),
            nb_items=2
        )
        result = list(gen)
        expected = [
            {'id': 1, 'name': 'foo', 'value': 0.5, 'constant': 42},
            {'id': 2, 'name': 'bar', 'value': 0.7, 'constant': 42}
        ]
        self.assertListEqual(result, expected)

    def test_2(self):
        gen = stream_generator(
            ('id', ),
            (self.make_id(), ),
            nb_items=-1
        )
        result = list(islice(gen, 3))
        self.assertListEqual(
            list(i['id'] for i in result),
            [1, 2, 3]
        )

    def test_3(self):
        gen = stream_generator(
            ('id', 'name'),
            (self.make_id(), self.make_name('foo')),
            nb_items=2
        )
        result = list(gen)
        expected = [
            {'id': 1, 'name': 'foo'},
            {'id': 2, 'name': None}
        ]
        self.assertListEqual(result, expected)


if __name__ == '__main__':
    run_tests(verbosity=2)

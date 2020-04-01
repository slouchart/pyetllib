from unittest import TestCase, main as run_tests

from src.pyetllib.etllib import groupby, aggregate, reduce
import functools


class TestGroupBy(TestCase):
    def setUp(self):
        self.data = [(1, 'foo'), (2, 'bar'), (1, 'spam'), (2, 'eggs')]

    def test_groupby_1(self):
        expected = {
            1: [(1, 'foo'), (1, 'spam')],
            2: [(2, 'bar'), (2, 'eggs')]
        }

        grouping = dict(
            groupby(
                lambda v: v[0],
                self.data
            )
        )

        self.assertDictEqual(expected, grouping)

    def test_aggregate_1(self):
        expected = {
            1: ['foo', 'spam'],
            2: ['bar', 'eggs']
        }
        grouping = dict(
            aggregate(
                lambda g: [i for k, i in g],
                groupby(
                    lambda v: v[0],
                    self.data
                )
            )
        )

        self.assertDictEqual(expected, grouping)

    def test_aggregate_2(self):
        expected = {1: 2, 2: 2}
        counts = dict(
            aggregate(
                functools.partial(reduce, lambda i, v: i+1, initial=0),
                groupby(lambda v: v[0], self.data)
            )
        )

        self.assertDictEqual(expected, counts)

    def test_aggregate_3(self):
        expected = {1: [3, 4], 2: [3, 4]}
        lengths = dict(
            aggregate(
                lambda g: list(map(len, (i[1] for i in g))),
                groupby(lambda v: v[0], self.data)
            )
        )

        self.assertDictEqual(expected, lengths)

    def test_aggregate_4(self):
        expected = {1: 7, 2: 7}
        sum_of_lengths = dict(
            aggregate(
                functools.partial(
                    reduce,
                    lambda l, s: l + len(s),
                    initial=0
                ),
                aggregate(
                    lambda g: list(i[1] for i in g),
                    groupby(lambda v: v[0], self.data)
                )
            )
        )

        self.assertDictEqual(expected, sum_of_lengths)

    def test_aggregate_5(self):
        result = dict(
            aggregate(None, groupby(lambda v: v[0], self.data))
        )
        expected = {
            1: [(1, 'foo'), (1, 'spam')],
            2: [(2, 'bar'), (2, 'eggs')]
        }
        self.assertDictEqual(expected, result)


if __name__ == '__main__':
    run_tests(verbosity=2)

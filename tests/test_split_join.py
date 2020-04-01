from unittest import TestCase, main as run_tests


from src.pyetllib.etllib import split, join


class TestSplitStream(TestCase):
    def setUp(self):
        self.iterable = [
            (i, 2*i) for i in range(2)
        ]

    def test_1(self):
        it1, it2 = split(lambda t: t, self.iterable)
        self.assertListEqual(
            list(i for i in range(2)),
            list(it1)
        )

        self.assertListEqual(
            list(2*i for i in range(2)),
            list(it2)
        )

    def test_2_not_enough_values(self):
        self.iterable.append((42, ))
        it1, it2 = split(lambda t: (t[0], t[1], ), self.iterable)
        with self.assertRaises(RuntimeError):
            _ = list(it1)

        with self.assertRaises(RuntimeError):
            _ = list(it2)

        it1, it2 = split(lambda t: (t[0], t[1]), self.iterable)
        with self.assertRaises(RuntimeError):
            _ = list(it2)

        with self.assertRaises(RuntimeError):
            _ = list(it1)

    def test_3_too_many_values(self):
        self.iterable.append((42, 'foo', 'bar'))
        it1, it2 = split(lambda t: t, self.iterable)
        with self.assertRaises(ValueError):
            _ = list(it1)

        with self.assertRaises(ValueError):
            _ = list(it2)

        it1, it2 = split(lambda t: t, self.iterable)
        with self.assertRaises(ValueError):
            _ = list(it2)

        with self.assertRaises(ValueError):
            _ = list(it1)

    def test_4_as_generators(self):
        it1, it2 = split(lambda t: t, self.iterable)
        g1, g2 = it1(), it2()
        result1, result2 = list(g1), list(g2)
        expected1, expected2 = list(i for i in range(2)), \
            list(2*i for i in range(2))

        self.assertListEqual(expected1, result1)
        self.assertListEqual(expected2, result2)

    def test_5_zero_length(self):
        its = split(lambda t: t, [])
        self.assertEqual(len(its), 0)

    def test_6_expected_length(self):
        self.iterable.append((42, 'foo', 'bar'))
        its = split(lambda t: t, self.iterable, expected_length=3)
        result = tuple(map(list, its))
        expected = (
            [0, 1, 42],
            [0, 2, 'foo'],
            ['bar']
        )
        self.assertTupleEqual(expected, result)


class TestJoin(TestCase):
    def setUp(self) -> None:
        self._3elem = list(range(3))
        self._2elem = list(range(2))
        self._0elem = []

    def test_1_same_length(self):
        result = list(
            join(self._3elem, self._3elem)
        )
        expected = list((i, i,) for i in range(3))
        self.assertListEqual(expected, result)

    def test_2_lengths_differ(self):
        result = list(
            join(self._3elem, self._2elem)
        )
        expected = list((i, i,) for i in range(2)) + [(2, None)]
        self.assertListEqual(expected, result)

    def test_3_first_iter_empty(self):
        result = list(
            join(self._0elem, self._2elem)
        )
        expected = list((None, i) for i in range(2))
        self.assertListEqual(expected, result)


if __name__ == '__main__':
    run_tests(verbosity=2)

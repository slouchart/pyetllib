from unittest import TestCase, main as run_tests


from src.pyetllib.etllib import filtertruefalse


class TestFilter(TestCase):

    def test_filter_1(self):
        data = list(range(5))

        _, evens = filtertruefalse(
            lambda x: bool(x % 2),
            data
        )
        self.assertListEqual(list(evens), [0, 2, 4])

    def test_filter_2(self):
        data = [10, 5, 6, 11, 21, 2, 7]
        digits, nondigits = filtertruefalse(
            lambda x: 0 <= x <= 9,
            data
        )
        self.assertSetEqual(set(digits), {5, 6, 7, 2})
        self.assertSetEqual(set(nondigits), {10, 11, 21})


if __name__ == '__main__':
    run_tests(verbosity=2)

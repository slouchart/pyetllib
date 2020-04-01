from unittest import TestCase, main as run_tests

from src.pyetllib.etllib import select


class TestRouter(TestCase):
    def setUp(self) -> None:
        self.data = [5, 9, 8, 50, 10, -3]

        self.rules = [
            (
                lambda x: 0 <= x <= 2,
                lambda x: 3 <= x <= 5,
                lambda x: 6 <= x <= 8,
                lambda x: 9 <= x <= 15,
                lambda x: x > 15
            ),
            (
                lambda x: 0 <= x <= 5,
                lambda x: 0 <= x < 9,
                lambda x: x >= 10,
                lambda x: x > 10
            ),
        ]

    def test_1(self):
        routes = tuple(
            map(
                list,
                select(self.rules[0], self.data)
            )
        )
        expected = (
            [], [5], [8], [9, 10], [50], [-3]
        )
        self.assertTupleEqual(routes, expected)

    def test_2(self):
        routes = tuple(
            map(
                list,
                select(self.rules[1], self.data)
            )
        )
        expected = (
            [5], [5, 8], [50, 10], [50], [9, -3]
        )
        self.assertTupleEqual(routes, expected)

    def test_3(self):
        routes = select(None, self.data)
        self.assertListEqual(list(routes[0]), self.data)
        self.assertListEqual(list(routes[1]), [])

    def test_4(self):
        routes = tuple(
            map(
                list,
                select(self.rules[0], self.data, strict=True)
            )
        )
        expected = (
            [], [5], [8], [9, 10], [50], [-3]
        )
        self.assertTupleEqual(routes, expected)

    def test_5(self):
        routes = tuple(
            map(
                list,
                select(self.rules[1], self.data, strict=True)
            )
        )
        expected = (
            [5], [8], [50, 10], [], [9, -3]
        )
        self.assertTupleEqual(routes, expected)


if __name__ == '__main__':
    run_tests(verbosity=2)

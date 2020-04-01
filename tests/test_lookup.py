from unittest import TestCase, main as run_tests

from src.pyetllib.etllib import lookup


class TestLookUp(TestCase):

    def setUp(self) -> None:
        self.data = list(range(5))
        self.even = [2*x for x in range(3)]

    def test_lookup_0(self):
        result = lookup(
            self.data,
            lookup_map={i: i for i in self.even},
            enable_rejects=False
        )
        self.assertListEqual(list(result), self.even)

    def test_lookup_1(self):
        result, rejects = lookup(
            self.data,
            lookup_map={i: i for i in self.even},
            enable_rejects=True
        )
        self.assertListEqual(list(result), self.even)
        self.assertListEqual(list(rejects), [1, 3])

    def test_lookup_2(self):
        result = lookup(self.data)
        self.assertListEqual(list(result), [])

    def test_lookup_3(self):
        result, rejects = lookup(self.data, enable_rejects=True)
        self.assertListEqual(list(result), [])
        self.assertListEqual(list(rejects), self.data)

    def test_lookup_4(self):
        result = lookup(
            self.data,
            lookup_map={i: i for i in self.even},
            merge=lambda v, m: (v, m == v),
        )
        expected = {
            0: True,
            2: True,
            4: True
        }
        self.assertDictEqual(dict(result), expected)

    def test_lookup_5(self):
        result = lookup(self.data,
                        lookup_map={i: i for i in self.even},
                        merge=True)
        expected = {
            0: 0,
            2: 2,
            4: 4
        }
        self.assertDictEqual(dict(result), expected)


if __name__ == '__main__':
    run_tests(verbosity=2)

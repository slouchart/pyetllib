from unittest import TestCase, main as run_tests

from src.pyetllib.etllib import replicate


class TestReplicate(TestCase):
    def test_1(self):
        data = list(range(2))
        it1, it2 = replicate(data)
        self.assertListEqual(data, list(it1))
        self.assertListEqual(data, list(it2))


if __name__ == '__main__':
    run_tests(verbosity=2)

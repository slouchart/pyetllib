from unittest import TestCase, main as run_tests

from toolz import curry

from itertools import repeat
from src.pyetllib.etllib import compose, mcompose
from src.pyetllib.etllib import pipeline, pipe_data_through, xargs
from src.pyetllib.etllib import pipable


def f1(x):
    return 2 * x


def f2(x):
    return x * x


class TestCompose1(TestCase):
    # composition of two f: x -> f(x)

    def test_1(self):
        f3 = compose(f2, f1)
        self.assertTrue(callable(f3))
        self.assertTrue(f3(1) == 4)


def fa(x, y):
    return x + y


def fb(x, y):
    return x, y


class TestMCompose(TestCase):
    def test_1(self):
        # composition of two f: x, y -> f(x, y)
        f4 = mcompose(fa, fb)
        self.assertTrue(callable(f4))
        self.assertTrue(f4(1, 1) == 2)


class TestPipeline(TestCase):

    def test_1(self):
        r = pipe_data_through(1, f1, f2, f1, f2)
        self.assertTrue(r == 64)

    def test_2(self):
        pp = pipeline(f1, f2, f1, f2)
        self.assertTrue(callable(pp))
        self.assertTrue(pp(1) == 64)


class TestXArgs(TestCase):

    def test_1(self):
        funcs = (
            lambda x: 2*x,
            lambda x: x/2
        )
        import operator
        g = xargs(operator.mul, funcs)
        self.assertTrue(g(1.0) == 1.0)

    def test_2(self):
        funcs = (
            lambda x: 2*x,
            lambda x: 3*x,
            lambda x: 4*x
        )
        g = xargs(sum, funcs, as_iterable=True)
        self.assertTrue(g(1, 2, 3) == 20)

    def test_3(self):
        funcs = repeat(lambda x: 2*x, 3)
        g = xargs(tuple, funcs, as_iterable=True)
        self.assertTrue(g(1) == (2, 2, 2))


@pipable
@curry
def t1(a, b):
    return a + b


@pipable
@curry
def t2(a, b):
    return a * b


class TestPipableCurried(TestCase):
    def test_1(self):
        tx = t1(2) | t2(3)
        result = tx(1)
        self.assertEqual(9, result)


if __name__ == '__main__':
    run_tests(verbosity=2)

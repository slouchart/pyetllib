from unittest import TestCase, main as run_tests


from src.pyetllib.etllib.curried import fextract, frename, fmap, fremove
from src.pyetllib.etllib.curried import flookup, freverse_lookup, fsplit

from src.pyetllib.etllib import pipable


class TestFExtract(TestCase):

    def test_1(self):
        data = {
            'f1': 1,
            'f2': 2,
            'f3': 3,
            'f4': 4
        }
        keys = ('f2', 'f4')
        expected = {
            'f2': 2,
            'f4': 4
        }
        result = fextract(keys, data)
        self.assertDictEqual(result, expected)


class TestFTranslate(TestCase):
    def setUp(self) -> None:
        self.data = {
            'f1': 1,
            'f2': 2,
            'f3': 3,
            'f4': 4
        }

    def test_1(self):

        keys = {
            'f1': 'e1',
            'f2': 'e2',
            'f3': 'e3',
            'f4': 'e4'
        }
        expected = {
            'e1': 1,
            'e2': 2,
            'e3': 3,
            'e4': 4
        }
        result = frename(keys, self.data)
        self.assertDictEqual(result, expected)

    def test_2(self):
        keys = {
            'f1': 'e1',
            'f2': 'e2',
        }
        expected = {
            'e1': 1,
            'e2': 2,
            'f3': 3,
            'f4': 4
        }
        result = frename(keys, self.data)
        self.assertDictEqual(result, expected)


class TestFMap(TestCase):
    def setUp(self) -> None:
        self.data = {
            1: 'foo',
            2: 'BAR'
        }

    def test_1(self):
        result = fmap((1, 2), (str.upper, str.lower), self.data)
        expected = {
            1: 'FOO',
            2: 'bar'
        }
        self.assertDictEqual(result, expected)

    def test_2(self):
        result = fmap((1, 2), (str.upper, ), self.data)
        expected = {
            1: 'FOO',
            2: 'BAR'
        }
        self.assertDictEqual(result, expected)

    def test_3(self):
        result = fmap((1, ), (str.upper, str.lower, ), self.data)
        expected = {
            1: 'FOO',
            2: 'BAR'
        }
        self.assertDictEqual(result, expected)

    def test_4(self):
        def _first(*args):
            return args[0]

        result = fmap((1, 2), (_first, _first), self.data, val_as_args=True)
        expected = {
            1: 'f',
            2: 'B'
        }
        self.assertDictEqual(result, expected)


class TestFRemove(TestCase):
    def setUp(self) -> None:
        self.data = {
            1: 'foo',
            2: 'bar'
        }

    def test_1(self):
        result = fremove((1, ), self.data)
        expected = {2: 'bar'}
        self.assertDictEqual(result, expected)

    def test_2(self):
        result = fremove((3, ), self.data)
        expected = self.data
        self.assertDictEqual(result, expected)


class TestFLookUp(TestCase):
    def setUp(self) -> None:
        self.data = {
            'id': 1
        }
        self.lookup_map = {
            1: 'foo'
        }
        self.lookup = flookup(self.lookup_map, ('id', ))

    def test_1(self):
        result = self.lookup(self.data)
        expected = {'id': 'foo'}
        self.assertDictEqual(expected, result)

    def test_2(self):
        self.data['id'] = 2
        result = self.lookup(self.data)
        expected = {'id': None}
        self.assertDictEqual(expected, result)

    def test_3(self):
        result = flookup(self.lookup_map, ('id', 'name'), self.data)
        expected = {'id': 'foo'}
        self.assertDictEqual(expected, result)


class TestFReverseLookUp(TestCase):
    def setUp(self) -> None:
        self.data = {'id': 1, 'name': 3}
        self.lookup_map = {
            'foo': (1, ),
            'bar': (3, ),
            'a_spam': (3, )
        }
        self.lookup = freverse_lookup(self.lookup_map, ('id', 'name'))

    def test_1(self):
        result = self.lookup(self.data)
        expected = {'id': 'foo', 'name': 'bar'}
        self.assertDictEqual(expected, result)

    def test_2(self):
        self.data['name'] = 2
        result = self.lookup(self.data)
        expected = {'id': 'foo', 'name': None}
        self.assertDictEqual(expected, result)

    def test_3(self):
        keys = ('id', 'name', 'foo')
        result = freverse_lookup(self.lookup_map, keys, self.data)
        expected = {'id': 'foo', 'name': 'bar'}
        self.assertDictEqual(expected, result)


class TestComposability(TestCase):
    def test_1(self):
        data = {
            'f1': 1,
            'f2': 'foo',
            'spam': 42
        }
        transform = pipable(fextract(('f1', 'f2', ))) \
            | pipable(frename({'f1': 'id', 'f2': 'name'}))

        result = transform(data)
        expected = {'id': 1, 'name': 'foo'}
        self.assertDictEqual(expected, result)


class TestFSplit(TestCase):
    def test_1(self):
        data = {
            'f1': 1,
            'f2': 'foo',
            'spam': 42
        }
        result = fsplit(('f1', 'f2'), data)
        expected = (
            {
                'f1': 1,
                'f2': 'foo',
            },
            {
                'spam': 42
            }
        )
        self.assertTupleEqual(expected, result)


if __name__ == '__main__':
    run_tests(verbosity=2)

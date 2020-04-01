from unittest import TestCase, main as run_tests

from collections import namedtuple
from itertools import repeat

from src.pyetllib.etllib import stream_converter


class TestStreamConverter(TestCase):
    def setUp(self) -> None:
        self.sample_dict = {
            'foo': 0,
            'bar': 42
        }
        self.sample_tuple = tuple(self.sample_dict.values())
        self.sample_namedtuple = namedtuple('T', self.sample_dict.keys())(
            *self.sample_tuple
        )

    def test_identity(self):
        with self.subTest("Identity tuple->tuple"):
            converter = stream_converter(tuple, tuple)
            result = converter(self.sample_tuple)
            expected = self.sample_tuple
            self.assertTupleEqual(expected, result)

        with self.subTest("Identity dict->dict"):
            converter = stream_converter(dict, dict)
            result = converter(self.sample_dict)
            expected = self.sample_dict
            self.assertDictEqual(expected, result)

        with self.subTest("Identity namedtuple->namedtuple"):
            converter = stream_converter(namedtuple, namedtuple)
            result = converter(self.sample_namedtuple)
            expected = self.sample_namedtuple
            self.assertEqual(expected, result)

    def test_tuple_to_dict(self):
        with self.subTest("str as keys"):
            field_names = tuple(self.sample_dict.keys())
            converter = stream_converter(tuple, dict, keys=field_names,
                                         key_type=str)
            result = converter(self.sample_tuple)
            expected = self.sample_dict
            self.assertDictEqual(expected, result)

        with self.subTest("int as keys"):
            converter = stream_converter(tuple, dict, key_type=int)
            result = converter(self.sample_tuple)
            expected = dict(
                zip(
                    range(len(self.sample_tuple)),
                    self.sample_tuple
                )
            )
            self.assertDictEqual(expected, result)

    def test_tuple_to_namedtuple(self):
        field_names = tuple(self.sample_dict.keys())
        converter = stream_converter(tuple, namedtuple, field_names)
        result = converter(self.sample_tuple)
        expected = self.sample_namedtuple
        self.assertEqual(expected, result)

    def test_dict_to_namedtuple(self):
        converter = stream_converter(dict, namedtuple)
        result = converter(self.sample_dict)
        expected = self.sample_namedtuple
        self.assertEqual(expected, result)

    def test_dict_to_tuple(self):
        converter = stream_converter(dict, tuple)
        result = converter(self.sample_dict)
        expected = self.sample_tuple
        self.assertTupleEqual(expected, result)

    def test_namedtuple_to_dict(self):
        converter = stream_converter(namedtuple, dict)
        result = converter(self.sample_namedtuple)
        expected = self.sample_dict
        self.assertDictEqual(expected, result)

    def test_namedtuple_to_tuple(self):
        converter = stream_converter(namedtuple, tuple)
        result = converter(self.sample_namedtuple)
        expected = self.sample_tuple
        self.assertTupleEqual(expected, result)

    def test_type_error_cases(self):
        sub_tests = list(zip(repeat(list, 3), (tuple, dict, namedtuple)))
        sub_tests += list(tuple(reversed(s)) for s in sub_tests)

        for sub_test in sub_tests:
            with self.subTest(f"converter {sub_test[0].__name__} "
                              f"-> {sub_test[1].__name__}"):
                with self.assertRaises(KeyError):
                    _ = stream_converter(*sub_test)

    def test_arg_error_cases(self):
        with self.subTest("arg error: no keys converting from tuple to dict"):
            with self.assertRaises(ValueError):
                _ = stream_converter(tuple, dict, (), key_type=str)

        with self.subTest("arg error: no keys converting "
                          "from tuple to namedtuple"):
            with self.assertRaises(ValueError):
                _ = stream_converter(tuple, namedtuple, ())

    def test_not_enough_keys(self):
        field_names = list(self.sample_dict.keys())[1:]
        with self.subTest('Not enough keys when tuple -> dict'):
            converter = stream_converter(tuple, dict,
                                         keys=field_names, key_type=str)
            result = converter(self.sample_tuple)
            expected = {'bar': 0}
            self.assertDictEqual(expected, result)

        with self.subTest('Not enough keys when tuple -> namedtuple'):
            converter = stream_converter(tuple, namedtuple, field_names)
            with self.assertRaises(TypeError):
                _ = converter(self.sample_tuple)

    def test_custom_dispatcher(self):
        stream_converter.dispatch(int, tuple)(
            lambda: lambda i: (i, )
        )
        converter = stream_converter(int, tuple)
        result = converter(42)
        expected = (42, )
        self.assertTupleEqual(expected, result)

    def test_composability(self):
        converter = stream_converter(dict, tuple) \
                    | stream_converter(tuple, dict, key_type=int) \
                    | stream_converter(dict, dict)

        result = converter(self.sample_dict)
        expected = {0: 0, 1: 42}
        self.assertDictEqual(expected, result)


if __name__ == '__main__':
    run_tests(verbosity=2)

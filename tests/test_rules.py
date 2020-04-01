from unittest import TestCase, main as run_tests

from itertools import repeat


from src.pyetllib.etllib import mapping_rule, set_field
from src.pyetllib.etllib import default_if_false, default_if_true
from src.pyetllib.etllib import default_if_none
from src.pyetllib.etllib import default_if_match, default_if_no_match
from src.pyetllib.etllib import default_if_equal, default_if_not_equal


class TestMappingRule(TestCase):
    def setUp(self) -> None:
        self.rules = (
            mapping_rule('cpu', default_if_false(bool, 'inconnu')),
            mapping_rule('ram', default_if_equal("#", 'inconnu')),
            mapping_rule('serialnumber', default_if_none('inconnu')),
        )
        self.data = {
            'cpu': '8-core',
            'ram': "#",
            'serialnumber': None
        }

    def test_rules_1(self):

        result = mapping_rule.apply(self.rules, self.data)
        expected = {
            'cpu': '8-core',
            'ram': 'inconnu',
            'serialnumber': 'inconnu'
        }
        self.assertDictEqual(result, expected)

    def test_rules_2(self):
        self.data['new_field'] = 'foo'
        result = mapping_rule.apply(self.rules, self.data)
        expected = {
            'cpu': '8-core',
            'ram': 'inconnu',
            'serialnumber': 'inconnu',
            'new_field': 'foo'
        }
        self.assertDictEqual(result, expected)

    def test_rules_3(self):

        @set_field(None)
        def func(_, t):
            return ':'.join(str(e[1]) for e in t)

        rules = (
            mapping_rule(
                'new_field',
                func,
                provide_all_values=True
            ),
            mapping_rule(
                'constant',
                set_field(3.14)
            )
        )
        result = mapping_rule.apply(rules, self.data)
        expected = {
            'cpu': '8-core',
            'ram': "#",
            'serialnumber': None,
            'new_field': '8-core:#:None',
            'constant': 3.14
        }
        self.assertDictEqual(expected, result)

    def test_rules_4(self):
        self.rules = (
            mapping_rule('ram', default_if_match(r"#", 'inconnu')),
        )
        result = mapping_rule.apply(self.rules, self.data)
        expected = {
            'cpu': '8-core',
            'ram': "inconnu",
            'serialnumber': None,
        }
        self.assertDictEqual(expected, result)

    def test_rules_5(self):
        self.rules = (
            mapping_rule('ram', default_if_no_match(r"[^#]", 'inconnu')),
        )
        result = mapping_rule.apply(self.rules, self.data)
        expected = {
            'cpu': '8-core',
            'ram': "inconnu",
            'serialnumber': None,
        }
        self.assertDictEqual(expected, result)

    def test_rules_6(self):
        self.rules = (
            mapping_rule('ram', default_if_no_match(r"[^#]", 'inconnu')),
        )
        result = mapping_rule.apply(self.rules, self.data)
        expected = {
            'cpu': '8-core',
            'ram': "inconnu",
            'serialnumber': None,
        }
        self.assertDictEqual(expected, result)

    def test_rules_7(self):
        self.rules = (
            mapping_rule('ram', default_if_true(
                lambda v: v == '#', 'inconnu')),
        )
        result = mapping_rule.apply(self.rules, self.data)
        expected = {
            'cpu': '8-core',
            'ram': "inconnu",
            'serialnumber': None,
        }
        self.assertDictEqual(expected, result)

    def test_rules_8(self):
        self.data['f1'] = '-'
        self.rules = (
            mapping_rule('f1', default_if_not_equal('FOO', 'FOO')),
        )
        result = mapping_rule.apply(self.rules, self.data)
        expected = {
            'cpu': '8-core',
            'ram': "#",
            'serialnumber': None,
            'f1': 'FOO'
        }
        self.assertDictEqual(expected, result)

    def test_rules_9(self):
        data = {'a': 1, 'b': 2}

        def _add(_, t):
            d = dict(t)
            return d['a'] + d['b']

        rules = (
            mapping_rule('a+b', _add, provide_all_values=True),
        )
        result = mapping_rule.apply(rules, data)
        expected = {'a': 1, 'b': 2, 'a+b': 3}
        self.assertDictEqual(result, expected)

    def test_rules_10(self):
        stream = repeat(self.data, 2)
        result = list(
            map(
                mapping_rule.get_apply_func(self.rules),
                stream
            )
        )
        expected = list(
            repeat(
                {
                    'cpu': '8-core',
                    'ram': 'inconnu',
                    'serialnumber': 'inconnu'
                },
                2
            )
        )
        self.assertListEqual(result, expected)


if __name__ == '__main__':
    run_tests(verbosity=2)

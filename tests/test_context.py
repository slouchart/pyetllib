from unittest import TestCase
from unittest import main as run_tests
from random import randint

from src.pyetllib.etllib.context import create_exec_context, ExecContext


class TestContext(TestCase):
    """Test cases collection for etllib.context.ExecContext"""

    def setUp(self) -> None:
        self.ctx = create_exec_context()

    def test_instance(self):
        self.assertIsNotNone(self.ctx)
        self.assertIsInstance(self.ctx, ExecContext)
        self.assertIsInstance(self.ctx, dict)

    def test_get_set_property(self):
        self.ctx.set_name('test')
        self.assertEqual(self.ctx.name, 'test')

    def test_dict_compat(self):
        self.ctx['name'] = 'test'
        self.assertEqual(self.ctx['name'], 'test')
        property_name = f'property_{randint(0, 42)}'
        with self.assertRaises(KeyError):
            self.assertIsNone(self.ctx[property_name])

    def test_does_not_have_all_properties(self):
        with self.assertRaises(KeyError):
            self.assertTrue(hasattr(self.ctx, f'property_{randint(0, 42)}'))

    def test_constructor_from_dict(self):
        dt = {
            'name': 'foo',
        }
        ctx = ExecContext(dt)
        self.assertIsNotNone(ctx.name)
        self.assertEqual(ctx.name, 'foo')

    def test_constructor_starred_params(self):
        dt = {
            'name': 'foo',
        }
        ctx = ExecContext(**dt)
        self.assertIsNotNone(ctx.name)
        self.assertEqual(ctx.name, 'foo')

    def test_method_has_property(self):
        ctx = ExecContext()
        self.assertTrue(hasattr(ctx, 'has_property'))
        self.assertFalse(ctx.has_property('spam'))

    def tearDown(self) -> None:
        self.ctx = None


if __name__ == '__main__':
    run_tests(verbosity=2)

from unittest import TestCase
from unittest import main as run_tests
import contextlib

import click
from click.testing import CliRunner
from src.pyetllib.etllib.context import ExecContext


from src.pyetllib.etllib.utils.utlcli import authentication
from src.pyetllib.etllib.utils.utlcli import bare_context_command_callback


assert_case = None


@click.command()
@click.option('-s', '--spam', default='baz')
@authentication()
@click.option('-b', '--bar', default='eggs')
@click.argument('data', default='yada')
def cmd_sink(ctx, *args, data, bar, spam, **kwargs):
    if assert_case is not None:
        assert callable(assert_case)
        assert_case(ctx)


class TestUtlCli(TestCase):
    @staticmethod
    @contextlib.contextmanager
    def set_assert_case(func) -> None:
        global assert_case
        assert_case = func
        yield
        assert_case = None

    def test_no_args(self):
        runner = CliRunner()

        def assert_case(ctx):
            pass

        with self.set_assert_case(assert_case):
            result = runner.invoke(cmd_sink, args=[])

        self.assertEqual(result.exit_code, 0)

    def test_utl_cli_pwd_env(self):
        opts = '-U foo -w'
        runner = CliRunner(env={'USER': 'foo', 'PASSWORD': 'yada'})

        def assert_call(ctx):
            self.assertIsNotNone(ctx.obj)
            self.assertIsInstance(ctx.obj, ExecContext)
            self.assertIn('username', ctx.obj)
            self.assertIn('password', ctx.obj)

        with self.set_assert_case(assert_call):
            result = runner.invoke(cmd_sink, opts)
        self.assertEqual(0, result.exit_code)

    def test_utl_cli_pwd_input(self):
        opts = '-U foo'
        runner = CliRunner()

        def assert_call(ctx):
            self.assertIsNotNone(ctx.obj)
            self.assertIsInstance(ctx.obj, ExecContext)
            self.assertIn('username', ctx.obj)
            self.assertIn('password', ctx.obj)

        with self.set_assert_case(assert_call):
            result = runner.invoke(cmd_sink, opts, input='yada')
        self.assertEqual(0, result.exit_code)

    def test_no_password(self):
        """Testing --no-password option without
        any valid password source (env/file)"""
        runner = CliRunner()
        result = runner.invoke(cmd_sink, args='-U foo -w')
        self.assertEqual(result.exit_code, 2)
        self.assertIn('no password file could be found',
                      result.output.lower())

    def test_no_password_env_provided(self):
        """Testing --no-password option with an ENV defined password"""
        runner = CliRunner()

        def assert_call(ctx):
            self.assertEqual(ctx.password, 'baz')
            self.assertEqual(ctx.username, 'foo')

        result = runner.invoke(cmd_sink, args='-U foo -w',
                               env={'USER': 'foo',
                                    'PASSWORD': 'baz'})

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output.lower(), '')

    def test_no_password_file_provided(self):
        """Testing --no-password option with a file defined password"""
        runner = CliRunner()

        def assert_call(ctx):
            self.assertEqual(ctx.password, 'baz')
            self.assertEqual(ctx.username, 'foo')

        with runner.isolated_filesystem():
            with open('.passwords', 'w') as f:
                f.write('foo:baz')

            result = runner.invoke(cmd_sink, args='-U foo -w',
                                   env={'USER': 'foo',
                                        'IDPASSFILE': '.passwords'})

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output.lower(), '')

    def test_input_password(self):
        runner = CliRunner()

        def assert_call(ctx):
            self.assertEqual(ctx.password, 'baz')
            self.assertEqual(ctx.username, 'foo')

        with self.subTest('Test with user provided through --username'):
            result = runner.invoke(cmd_sink, args='-U foo', input='baz')

            self.assertEqual(result.exit_code, 0)
            self.assertIn('password for', result.output.lower())

        with self.subTest('Test with user provided through ENV'):
            result = runner.invoke(cmd_sink, args='',
                                   input='baz', env={'USER': 'foo'})

            self.assertEqual(result.exit_code, 0)
            self.assertIn('password for', result.output.lower())

        with self.subTest('Test precedence of --username of ENV.user'):
            result = runner.invoke(cmd_sink, args='-U foo', input='baz',
                                   env={'USER': 'spam'})

            self.assertEqual(result.exit_code, 0)
            self.assertIn('password for', result.output.lower())


@click.command()
@click.pass_context
@bare_context_command_callback
def cmd_callback_1(context):
    assert False, f"context is {context}"


@click.command()
@click.pass_obj
@click.pass_context
@click.option('-b', is_flag=True, default=False)
@click.argument('arg')
@bare_context_command_callback
def cmd_callback_2(context):
    click.echo(context)


def swap_name_value(ctx, param, value):
    ctx.ensure_object(ExecContext)
    ctx.obj[value] = param.name


@click.command()
@click.pass_context
@click.argument('arg', callback=swap_name_value)
@bare_context_command_callback
def cmd_callback_3(context):
    click.echo(context)


class TestBareContextCmdCallback(TestCase):
    def test_no_args(self):
        runner = CliRunner()
        with self.assertRaises(AssertionError) as cm:
            _ = runner.invoke(cmd_callback_1, catch_exceptions=False)

        self.assertEqual('context is {}', str(cm.exception))

    def test_arg_and_opt(self):
        runner = CliRunner()
        opts = '-b DATA'
        result = runner.invoke(cmd_callback_2, opts)
        expected = {
            'b': True,
            'arg': 'DATA'
        }
        self.assertEqual(str(expected), result.output.strip())

    def test_ensure_obj(self):
        runner = CliRunner()
        opts = 'DATA'
        result = runner.invoke(cmd_callback_3, opts)
        expected = {
            'arg': None,
            'DATA': 'arg',
        }
        self.assertEqual(str(expected), result.output.strip())


if __name__ == '__main__':
    run_tests(verbosity=2)

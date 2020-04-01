from unittest import TestCase
from unittest.mock import patch
from unittest import main as run_tests

import os
import io

from src.pyetllib.etllib.utils.utlpwd import PasswordReader


class TestNominalUtlPwd(TestCase):
    def setUp(self):
        self.reader = PasswordReader(envvar_prefix='TEST_')

        self.environ = {
            'TEST_USER': 'foo',
            'TEST_PASSWORD': 'spam',
            'TEST_IDPASSFILE': '<file>'
        }
        os.environ.update(self.environ)

    def mock_open(self, *args, **kwargs):
        self.password_file = io.StringIO(initial_value='foo:spam')
        return self.password_file

    def test_read_password_from_env(self):
        pwd = self.reader.read_password_from_env('foo')
        self.assertEqual(pwd, self.environ.get('TEST_PASSWORD'))

    def test_read_password_from_file(self):
        with patch('src.pyetllib.etllib.utils.utlpwd.io.open',
                   new=self.mock_open):
            pwd = self.reader.read_password_from_file('foo')
            self.assertEqual(pwd, self.environ.get('TEST_PASSWORD'))

    def tearDown(self) -> None:
        for envvar in self.environ.keys():
            del os.environ[envvar]


class TestUtlPwdErrors(TestCase):
    def setUp(self) -> None:
        self.reader = PasswordReader(envvar_prefix='FAIL_')

    def test_variables(self):
        self.assertEqual(self.reader.envvars.username, 'FAIL_USER')
        self.assertEqual(self.reader.envvars.password, 'FAIL_PASSWORD')
        self.assertEqual(self.reader.envvars.passfile, 'FAIL_IDPASSFILE')

    def mock_open(self, *args, **kwargs):
        self.password_file = io.StringIO(initial_value='bar:baz')
        return self.password_file

    def test_unset_user(self):
        with self.assertRaises(RuntimeError) as cm:
            _ = self.reader.read_password_from_env('foo')

        expected_msg = 'environment variable FAIL_USER is not set'
        self.assertIn(expected_msg, str(cm.exception))

    def test_wrong_user(self):
        os.environ.setdefault(self.reader.envvars.username, 'foo')
        os.environ.setdefault(self.reader.envvars.password, 'bar')
        with self.assertRaises(ValueError) as cm:
            _ = self.reader.read_password_from_env('bar')

        expected_msg = 'The provided username does not match ' \
                       'the username set in the environment'
        self.assertIn(expected_msg, str(cm.exception))
        del os.environ[self.reader.envvars.username]
        del os.environ[self.reader.envvars.password]

    def test_unset_pwd(self):
        os.environ.setdefault(self.reader.envvars.username, 'foo')
        with self.assertRaises(RuntimeError) as cm:
            _ = self.reader.read_password_from_env('foo')

        self.assertIn('environment variable FAIL_PASSWORD '
                      'is not set', str(cm.exception))
        del os.environ[self.reader.envvars.username]

    def test_unset_passfile(self):
        with self.assertRaises(RuntimeError) as cm:
            _ = self.reader.read_password_from_file('foo')

        self.assertIn('environment variable FAIL_IDPASSFILE '
                      'is not set', str(cm.exception))

    def test_unknown_credentials(self):
        os.environ.setdefault(self.reader.envvars.passfile, '<file>')
        with patch('src.pyetllib.etllib.utils.utlpwd.io.open',
                   new=self.mock_open):
            with self.assertRaises(RuntimeError) as cm:
                _ = self.reader.read_password_from_file('foo')

            self.assertIn('The user foo does not have any credentials '
                          'set in <file>', str(cm.exception))
        del os.environ[self.reader.envvars.passfile]


if __name__ == '__main__':
    run_tests(verbosity=2)

__all__ = [
    'PasswordReader',
]

import os
import re
import io
from collections import namedtuple


class PasswordReader:
    envvar_user = 'USER'
    envvar_password = 'PASSWORD'
    envvar_passfile = 'IDPASSFILE'

    def __init__(self, envvar_prefix='', envvar_user='',
                 envvar_password='', envvar_passfile=''):
        self.envvars = namedtuple('Envars', 'username, password, passfile')
        self.envvars.username = envvar_prefix + (envvar_user
                                                 or self.envvar_user)
        self.envvars.password = envvar_prefix + (envvar_password
                                                 or self.envvar_password)
        self.envvars.passfile = envvar_prefix + (envvar_passfile
                                                 or self.envvar_passfile)

    def read_password_from_env(self, expected_user):
        assert expected_user is not None

        if self.envvars.username not in os.environ:
            raise RuntimeError(f'environment variable {self.envvars.username} '
                               f'is not set')

        if self.envvars.password not in os.environ:
            raise RuntimeError(f'environment variable {self.envvars.password} '
                               f'is not set')

        password = os.environ.get(self.envvars.password)
        if expected_user == os.environ.get(self.envvars.username):
            return password
        else:
            raise ValueError('The provided username does not match '
                             'the username set in the environment')

    def read_password_from_file(self, username):
        if self.envvars.passfile not in os.environ:
            raise RuntimeError(f'environment variable {self.envvars.passfile} '
                               f'is not set')

        password_file = os.environ.get(self.envvars.passfile)
        pattern = re.compile(r'^'
                             + re.escape(username)
                             + ':(?P<password>[^:\\s]+)$')
        with io.open(password_file, mode="r", encoding="utf-8") as f:
            for line in f:
                m = pattern.match(line)
                if m:
                    return m.group('password')
            else:
                raise RuntimeError(f'The user {username} does not have '
                                   f'any credentials set in {password_file}')

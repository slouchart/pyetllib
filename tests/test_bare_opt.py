from unittest import TestCase
from unittest import main as run_tests

from pathlib import Path
from click.testing import CliRunner


from src.pyetllib.etlskel.cli import etlskel


class TestBareOption(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.root_dir = 'dummy'

    def assertPathPresent(self, *pathparts):
        self.assertTrue(
            Path().joinpath(*pathparts).exists(),
            f"Path {Path().joinpath(*pathparts)} does not exist "
            f"in the current directory"
        )

    def assertPathNotPresent(self, *pathparts):
        self.assertFalse(
            Path().joinpath(*pathparts).exists(),
            f"Path {Path().joinpath(*pathparts)} does exist "
            f"in the current directory"
        )

    def test_bare_option_false(self):
        opts = self.root_dir
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                etlskel,
                opts,
                input='y'
            )
            self.assertEqual(result.exit_code, 0)
            self.assertPathPresent(self.root_dir, 'tox.ini')
            self.assertPathPresent(self.root_dir, '.gitignore')

    def test_bare_option_true(self):
        opts = '--bare ' + self.root_dir
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                etlskel,
                opts,
                input='y'
            )
            self.assertEqual(result.exit_code, 0)
            self.assertPathNotPresent(self.root_dir, 'tox.ini')
            self.assertPathNotPresent(self.root_dir, '.gitignore')


if __name__ == '__main__':
    run_tests(verbosity=2)

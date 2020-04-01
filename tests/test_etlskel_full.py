from unittest import TestCase
from unittest import main as run_tests

from pathlib import Path
from click.testing import CliRunner

from src.pyetllib.etlskel.cli import etlskel


class TestEndToEndEtlSkel(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.root_dir = 'to_be_removed'

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

    def filesystem_cm(self):
        return self.runner.isolated_filesystem()

    def invoke_cli(self, opts):
        return self.runner.invoke(etlskel, opts + [self.root_dir], input='y')

    def test_basic_no_opts(self):
        options = []
        with self.filesystem_cm():
            _ = self.invoke_cli(options)
            self.assertPathPresent(self.root_dir)
            self.assertPathPresent(self.root_dir, self.root_dir)
            self.assertPathPresent(self.root_dir, self.root_dir,
                                   'templates')
            self.assertPathPresent(self.root_dir, 'tests')
            self.assertPathPresent(self.root_dir, 'setup.py')
            self.assertPathPresent(self.root_dir, 'README.md')
            self.assertPathPresent(self.root_dir, 'MANIFEST.in')

    def test_no_template(self):
        options = ['--no-template-dir']
        with self.filesystem_cm():
            _ = self.invoke_cli(options)
            self.assertPathPresent(self.root_dir)
            self.assertPathPresent(self.root_dir, self.root_dir)
            self.assertPathNotPresent(self.root_dir, self.root_dir,
                                      'templates')
            self.assertPathPresent(self.root_dir, 'tests')
            self.assertPathPresent(self.root_dir, 'setup.py')
            self.assertPathPresent(self.root_dir, 'README.md')
            self.assertPathNotPresent(self.root_dir, 'MANIFEST.in')

    def test_no_test(self):
        options = ['--no-test-package']
        with self.filesystem_cm():
            _ = self.invoke_cli(options)
            self.assertPathPresent(self.root_dir)
            self.assertPathPresent(self.root_dir, self.root_dir)
            self.assertPathPresent(self.root_dir, self.root_dir,
                                   'templates')
            self.assertPathNotPresent(self.root_dir, 'tests')
            self.assertPathPresent(self.root_dir, 'setup.py')
            self.assertPathPresent(self.root_dir, 'README.md')
            self.assertPathPresent(self.root_dir, 'MANIFEST.in')

    def test_no_template_no_test(self):
        options = ['--no-test-package', '--no-template-dir']
        with self.filesystem_cm():
            _ = self.invoke_cli(options)
            self.assertPathPresent(self.root_dir)
            self.assertPathPresent(self.root_dir, self.root_dir)
            self.assertPathNotPresent(self.root_dir, self.root_dir,
                                      'templates')
            self.assertPathNotPresent(self.root_dir, 'tests')
            self.assertPathPresent(self.root_dir, 'setup.py')
            self.assertPathPresent(self.root_dir, 'README.md')
            self.assertPathNotPresent(self.root_dir, 'MANIFEST.in')

    def test_with_src_dir(self):
        options = ['-s']
        with self.filesystem_cm():
            _ = self.invoke_cli(options)
            self.assertPathPresent(self.root_dir)
            self.assertPathPresent(self.root_dir, 'src')
            self.assertPathNotPresent(self.root_dir, self.root_dir)
            self.assertPathPresent(self.root_dir, 'src', self.root_dir)
            self.assertPathPresent(self.root_dir, 'src', self.root_dir,
                                   'templates')
            self.assertPathPresent(self.root_dir, 'tests')
            self.assertPathPresent(self.root_dir, 'setup.py')
            self.assertPathPresent(self.root_dir, 'README.md')
            self.assertPathPresent(self.root_dir, 'MANIFEST.in')

    def test_alt_package_name(self):
        package = 'foo'
        options = ['-p', package]
        with self.filesystem_cm():
            _ = self.invoke_cli(options)
            self.assertPathPresent(self.root_dir)
            self.assertPathNotPresent(self.root_dir, self.root_dir)
            self.assertPathPresent(self.root_dir, package)
            self.assertPathPresent(self.root_dir, package, 'templates')
            self.assertPathPresent(self.root_dir, 'tests')
            self.assertPathPresent(self.root_dir, 'setup.py')
            self.assertPathPresent(self.root_dir, 'README.md')
            self.assertPathPresent(self.root_dir, 'MANIFEST.in')

    def all_opt_together(self):
        package = 'foo'
        options = [
            '-p', package,
            '-s',
            '--no-test-package',
            '--no-template-dir'
        ]
        with self.filesystem_cm():
            _ = self.invoke_cli(options)
            self.assertPathPresent(self.root_dir)
            self.assertPathNotPresent(self.root_dir, self.root_dir)
            self.assertPathNotPresent(self.root_dir, package)
            self.assertPathNotPresent(self.root_dir, package, 'templates')
            self.assertPathPresent(self.root_dir, 'src', package)
            self.assertPathNotPresent(self.root_dir, 'src', package,
                                      'templates')
            self.assertPathNotPresent(self.root_dir, 'tests')
            self.assertPathPresent(self.root_dir, 'setup.py')
            self.assertPathPresent(self.root_dir, 'README.md')
            self.assertPathNotPresent(self.root_dir, 'MANIFEST.in')

    def tearDown(self) -> None:
        pass


if __name__ == '__main__':
    run_tests(verbosity=2)

from click.testing import CliRunner
from unittest import TestCase
from unittest import main as run_tests
from unittest import mock


from src.pyetllib.etllib.commands import AlwaysSucceeds
from src.pyetllib.etlskel.cli import etlskel


class TestCLI(TestCase):
    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(etlskel, args='--help')
        self.assertEqual(result.exit_code, 0)
        self.assertIn('usage', result.output.lower())

    def test_cli(self):
        runner = CliRunner()

        def mock_create_skel_1(project_name,
                               main_package_name,
                               create_template_dir,
                               create_source_dir,
                               no_test_package,
                               bare):
            self.assertEqual(project_name, 'my_project')
            self.assertEqual(main_package_name, 'etltest')
            self.assertFalse(create_template_dir)
            self.assertFalse(create_source_dir)
            self.assertFalse(no_test_package)
            self.assertFalse(bare)
            return AlwaysSucceeds(), ''

        def mock_create_skel_2(project_name,
                               main_package_name,
                               create_template_dir,
                               create_source_dir,
                               no_test_package,
                               bare):
            self.assertEqual(project_name, 'my_project')
            self.assertIsNone(main_package_name)
            self.assertTrue(create_template_dir)
            self.assertFalse(create_source_dir)
            self.assertFalse(no_test_package)
            self.assertFalse(bare)
            return AlwaysSucceeds(), ''

        with self.subTest("no template alternative package name"):
            with mock.patch('src.pyetllib.etlskel.cli.create_skeleton',
                            new=mock.Mock(wraps=mock_create_skel_1)):
                opts = '--package-name=etltest --no-template-dir my_project'
                result = runner.invoke(etlskel, args=opts, input='y')
                self.assertEqual(result.exit_code, 0)

        with self.subTest("default (no template, package_name=project_name"):
            with mock.patch('src.pyetllib.etlskel.cli.create_skeleton',
                            new=mock.Mock(wraps=mock_create_skel_2)):
                result = runner.invoke(etlskel, args='my_project', input='y')
                self.assertEqual(result.exit_code, 0)


if __name__ == '__main__':
    run_tests()

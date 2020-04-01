from unittest import TestCase
from unittest import main as run_tests

import pkg_resources
from click.testing import CliRunner
import click

from src.pyetllib.launcher.cli import pyetl


@click.command()
def plgtest():
    click.echo('Everything went well.')


class TestPluginCLI(TestCase):
    def setUp(self) -> None:
        dist = pkg_resources.Distribution(__file__)
        ep_dcl = 'test = tests.test_plugin_cli:plgtest'
        ep = pkg_resources.EntryPoint.parse(ep_dcl, dist=dist)
        dist._ep_map = {'pyetl_plugins': {'test': ep}}
        pkg_resources.working_set.add(dist)

    def test_cli(self):
        """Tests basic invocation with --help option"""
        runner = CliRunner()
        result = runner.invoke(pyetl, ['run', '--help'])
        self.assertEqual(result.exit_code, 0)

    def test_plugin_subcommand(self):
        """Tests the main functionality which
        is running a registered plugin"""
        runner = CliRunner()
        result = runner.invoke(pyetl, ['run', 'test'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Everything went well.', result.output)

    def test_missing_plugin(self):
        """Tests involving a missing plugin. Must not bark"""
        runner = CliRunner()
        result = runner.invoke(pyetl, ['run', 'missing'])
        self.assertEqual(result.exit_code, 2)
        self.assertIn('could not be loaded', result.output)

    def tearDown(self) -> None:
        wk = pkg_resources.working_set
        dist = pkg_resources.Distribution(__file__)
        wk.entries.remove(dist.location)
        del wk.entry_keys[dist.location]
        del wk.by_key[dist.key]


class TestShowPlugins(TestCase):
    def setUp(self) -> None:
        dist = pkg_resources.Distribution(__file__)
        ep_map = dict()
        ep_dcl_fmt = 'test{0} = tests.test_plugin_cli:plgtest'
        for inx in range(3):
            ep = pkg_resources.EntryPoint.parse(ep_dcl_fmt.format(inx),
                                                dist=dist)
            ep_map[ep.name] = ep
        dist._ep_map = {'pyetl_plugins': ep_map}
        pkg_resources.working_set.add(dist)

    def test_show_plugins(self):
        """Tests the display of the list of installed plugins"""
        runner = CliRunner()
        result = runner.invoke(pyetl, ['show', 'plugins'])
        self.assertEqual(result.exit_code, 0)
        for inx in range(3):
            self.assertIn(f'test{inx}', result.output.strip())

    def tearDown(self) -> None:
        wk = pkg_resources.working_set
        dist = pkg_resources.Distribution(__file__)
        wk.entries.remove(dist.location)
        del wk.entry_keys[dist.location]
        del wk.by_key[dist.key]


class TestShowNoPlugin(TestCase):
    def test_show_no_plugin(self):
        """Tests displaying an empty plugin list"""
        runner = CliRunner()
        result = runner.invoke(pyetl, ['show', 'plugins'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('No plugin installed', result.output)


if __name__ == '__main__':
    run_tests(verbosity=2)

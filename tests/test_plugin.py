from unittest import TestCase
from unittest import main as run_tests
import pkg_resources

import click
from click.testing import CliRunner
from src.pyetllib.launcher.plugins import PluginRegistry
from src.pyetllib.launcher.plugins import BrokenPlugin, MissingPlugin


@click.command()
def plgtest(*args, **kwargs):
    click.echo('some output')
    return True


def not_a_command():
    ...


class TestPluginNominal(TestCase):
    def setUp(self):
        dist = pkg_resources.Distribution(__file__)
        ep_map = dict()
        ep_dcl_fmt = 'test{0} = tests.test_plugin:plgtest'
        for inx in range(3):
            ep = pkg_resources.EntryPoint.parse(ep_dcl_fmt.format(inx),
                                                dist=dist)
            ep_map[ep.name] = ep
        dist._ep_map = {'plugin_nominal': ep_map}
        pkg_resources.working_set.add(dist)
        self.registry = PluginRegistry.instance('plugin_nominal')

    def test_instantiate(self):
        registry = self.registry
        self.assertIsNotNone(registry)
        self.assertIsInstance(registry, PluginRegistry)
        self.assertEqual(registry.plugins_group_name, 'plugin_nominal')

    def test_list_plugins(self):
        registry = self.registry
        plugins = registry.get_plugins_list()
        self.assertListEqual(plugins, ['test0', 'test1', 'test2'])

    def test_iter_plugin(self):
        registry = self.registry
        self.assertTrue(hasattr(registry, '__iter__'))
        plugins = [plg for plg in registry]
        self.assertListEqual(plugins, ['test0', 'test1', 'test2'])

    def test_find_plugin(self):
        registry = self.registry
        plugin = registry.find_plugin_by_name('test0')
        self.assertIsNotNone(plugin)

    def test_get_plugin(self):
        registry = self.registry
        plugin = registry['test0']
        self.assertIsNotNone(plugin)

    def test_invoke_found_plugin(self):
        registry = self.registry
        cmd = registry.load_command_from_plugin('test0')
        self.assertIsNotNone(cmd)
        self.assertIsInstance(cmd, click.Command)
        result = CliRunner().invoke(cmd)
        self.assertEqual(result.exit_code, 0)
        self.assertIn('some output', result.output)

    def test_missing_plugin(self):
        registry = self.registry
        cmd = registry.load_command_from_plugin('testX')
        self.assertIsNotNone(cmd)
        self.assertIsInstance(cmd, click.Command)
        self.assertIsInstance(cmd, MissingPlugin)
        result = CliRunner().invoke(cmd)
        self.assertEqual(result.exit_code, 2)
        self.assertIn("Warning: entry point 'testX' "
                      "could not be loaded", result.output)

    def test_missing_plugin_exception(self):
        registry = self.registry
        with self.assertRaises(KeyError):
            _ = registry['missing_plugin']

    def tearDown(self) -> None:
        del self.registry
        wk = pkg_resources.working_set
        dist = pkg_resources.Distribution(__file__)
        wk.entries.remove(dist.location)
        del wk.entry_keys[dist.location]
        del wk.by_key[dist.key]


class TestBrokenPluginBadCommand(TestCase):
    def setUp(self) -> None:
        dist = pkg_resources.Distribution(__file__)
        ep_map = dict()
        ep_dcl = 'test = tests.test_plugin:not_a_command'
        ep1 = pkg_resources.EntryPoint.parse(ep_dcl, dist=dist)
        ep_map[ep1.name] = ep1

        dist._ep_map = {'broken_plugins': ep_map}
        pkg_resources.working_set.add(dist)

        self.registry = PluginRegistry.instance('broken_plugins')

    def test_broken_plugin_reason_bad_command(self):
        registry = self.registry
        cmd = registry.load_command_from_plugin('test')
        self.assertIsNotNone(cmd)
        self.assertIsInstance(cmd, BrokenPlugin)
        self.assertIn('not an instance', cmd.reason)
        result = CliRunner().invoke(cmd)
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Warning: entry point 'test' "
                      "could not be loaded", result.output)

    def tearDown(self) -> None:
        del self.registry
        wk = pkg_resources.working_set
        dist = pkg_resources.Distribution(__file__)
        wk.entries.remove(dist.location)
        del wk.entry_keys[dist.location]
        del wk.by_key[dist.key]


class TestBrokenCommandBadModule(TestCase):
    def setUp(self) -> None:
        dist = pkg_resources.Distribution(__file__)
        ep_map = dict()
        ep_dcl = 'test = tests.not_a_module:not_a_command'
        ep1 = pkg_resources.EntryPoint.parse(ep_dcl, dist=dist)
        ep_map[ep1.name] = ep1

        dist._ep_map = {'broken_plugins': ep_map}
        pkg_resources.working_set.add(dist)

        self.registry = PluginRegistry.instance('broken_plugins')

    def test_broken_plugin_reason_cannot_import(self):
        registry = self.registry
        cmd = registry.load_command_from_plugin('test')
        self.assertIsNotNone(cmd)
        self.assertIsInstance(cmd, BrokenPlugin)
        self.assertIn('No module', cmd.reason)

    def tearDown(self) -> None:
        del self.registry

        wk = pkg_resources.working_set
        dist = pkg_resources.Distribution(__file__)
        wk.entries.remove(dist.location)
        del wk.entry_keys[dist.location]
        del wk.by_key[dist.key]


class TestWrongInstantiation(TestCase):
    def test_direct_instantiation(self):
        registry = PluginRegistry()
        self.assertFalse(hasattr(registry, 'plugins_group_name'))

        with self.assertRaises(RuntimeError) as cm:
            PluginRegistry.validate_register(registry)
        self.assertIn("expected instance variable 'plugins_group_name' "
                      "not found", str(cm.exception))


class MockRegistry(PluginRegistry):
    pass


class TestRegistrySubClass(TestCase):
    def setUp(self) -> None:
        dist = pkg_resources.Distribution(__file__)
        ep_map = dict()
        ep_dcl_fmt = 'test{0} = tests.test_plugin:plgtest'
        for inx in range(3):
            ep = pkg_resources.EntryPoint.parse(ep_dcl_fmt.format(inx),
                                                dist=dist)
            ep_map[ep.name] = ep
        dist._ep_map = {'dummy_group': ep_map}
        pkg_resources.working_set.add(dist)

        self.registry = MockRegistry.instance('dummy_group')

    def test_valid_plugin_group_name(self):
        registry = self.registry
        self.assertIsNotNone(registry)
        self.assertIsInstance(registry, MockRegistry)
        self.assertTrue(hasattr(registry, 'plugins_group_name'))
        self.assertListEqual(registry.get_plugins_list(),
                             ['test0', 'test1', 'test2'])

    def tearDown(self) -> None:
        del self.registry

        wk = pkg_resources.working_set
        dist = pkg_resources.Distribution(__file__)
        wk.entries.remove(dist.location)
        del wk.entry_keys[dist.location]
        del wk.by_key[dist.key]


class TestEmptyPluginGroup(TestCase):
    def test_empty_group_name(self):
        with self.assertRaises(RuntimeError):
            _ = PluginRegistry.instance("")


class TestWeakRefAndReset(TestCase):
    def setUp(self) -> None:
        self.registries = []
        self.registries.append(PluginRegistry.instance('dummy_group_1'))
        self.registries.append(PluginRegistry.instance('dummy_group_2'))

    def test_reset_registries(self):
        self.assertIsNotNone(PluginRegistry.instance('dummy_group_1'))
        self.assertIsNotNone(PluginRegistry.instance('dummy_group_1'))
        PluginRegistry.reset_registries()
        self.assertFalse(PluginRegistry.exists('dummy_group_1'))
        self.assertFalse(PluginRegistry.exists('dummy_group_2'))


if __name__ == '__main__':
    run_tests(verbosity=2)

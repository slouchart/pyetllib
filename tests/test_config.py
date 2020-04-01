from unittest import TestCase, main as run_tests
from unittest import skip
from pathlib import Path
import io
import os
import pkgutil

from src.pyetllib.etllib.context import ExecContext
from src.pyetllib.etllib.config import PluginConfig
from src.pyetllib.etllib.config import (
    ConfigTextLoader,
    ConfigFileLoader,
    ConfigPackageLoader,
)


class TestConfig(TestCase):
    def setUp(self) -> None:
        self.fixtures = dict()
        self.fixtures['nominal'] = """[pyetl]
    a_key = 42

[plugins]
    another_key = 'foo'
    [plugins.dnsgen]
        url = 'spam.org'
    [plugins.dhcp]
        url = 'foo.com'
    [plugins.pcaudit]
        url = 'bar.ru'
    """
        self.fixtures['no_app_section'] = """foo = 'bar'
        """
        self.fixtures['no_section_plugins'] = """[pyetl]
        """
        self.fixtures['no_plugin_section'] = """[pyetl]
        [plugins]
        """

        self.fixtures['multiple_datasources'] = """[pyetl]


[plugins]

    [plugins.dnsgen]

    [plugins.dhcp]

    [plugins.pcaudit]
    [plugins.pcaudit.datasources]
        [plugins.pcaudit.datasources.itop]
            username = 'foo'
        [plugins.pcaudit.datasources.opsi]
            username = 'bar'
    """

        self.file = Path("~").expanduser().joinpath('pyetl.config.toml')

    def set_file_with(self, content_id):
        with io.open(self.file, mode='w', encoding='utf-8') as f:
            f.writelines(self.fixtures[content_id])

    def test_config_plugin(self):

        self.set_file_with('nominal')

        config = PluginConfig('pyetl', 'pcaudit', ConfigFileLoader)
        config = config.load()
        self.assertIsInstance(config, dict)
        self.assertEqual(2, len(config))
        self.assertIn('a_key', config)
        self.assertIn('url', config)
        self.assertEqual(config['url'], 'bar.ru')

    def test_bad_structure_no_app_section(self):

        self.set_file_with('no_app_section')
        config = PluginConfig('pyetl', 'pcaudit', ConfigFileLoader)
        with self.assertRaises(RuntimeError) as cm:
            _ = config.load()
        self.assertIn(
            'Invalid structure of the configuration file '
            'for application pyetl: no section [pyetl]',
            str(cm.exception)
        )

    def test_bad_structure_no_plugins_section(self):

        self.set_file_with('no_section_plugins')
        config = PluginConfig('pyetl', 'pcaudit', ConfigFileLoader)
        with self.assertRaises(RuntimeError) as cm:
            _ = config.load()
        self.assertIn(
            "Invalid structure of the configuration file for application "
            "pyetl: no section [plugins] or plugin's section "
            "[plugins.pcaudit]",
            str(cm.exception)
        )

    def test_bad_structure_no_section_for_plugin(self):

        self.set_file_with('no_plugin_section')
        config = PluginConfig('pyetl', 'pcaudit', ConfigFileLoader)
        with self.assertRaises(RuntimeError) as cm:
            _ = config.load()

        self.assertIn(
            "Invalid structure of the configuration file for application "
            "pyetl: no section [plugins] or plugin's section "
            "[plugins.pcaudit]",
            str(cm.exception)
        )

    def test_file_not_found(self):
        config = PluginConfig('pyetl', 'pcaudit', ConfigFileLoader)
        with self.assertRaises(FileNotFoundError) as cm:
            _ = config.load()

        self.assertIn(
            "No file named 'pyetl.config.toml' "
            "can be located at these locations:",
            str(cm.exception)
        )

    def tearDown(self) -> None:
        if self.file.exists():
            os.remove(self.file)

    def test_multiple_datasources(self):
        self.set_file_with('multiple_datasources')
        config = PluginConfig('pyetl', 'pcaudit', ConfigFileLoader)
        config = config.load()
        self.assertIn('datasources', config)
        for section in ('opsi', 'itop'):
            self.assertIn(section, config['datasources'])
            self.assertIn('username', config['datasources'][section])


def load_toml_text(resource_name):
    bin_data = pkgutil.get_data('tests.fixtures', resource_name)
    return bin_data.decode()


class TestLocalConfig(TestCase):
    def setUp(self) -> None:
        self.full_data = load_toml_text('pyetl.config.toml')

    def test_1(self):
        config = PluginConfig('pyetl', 'pcaudit', ConfigTextLoader)
        ctx = ExecContext.from_dict(config.load(self.full_data))
        result = ctx["itop"]
        expected = {
            'username': 'bot.test',
            'password': 'Mr9MS8WvJ6GdJZbe',
            'url': 'https://itsm-dev.escolan.recia.fr',
            'version': '1.3',
        }
        self.assertDictEqual(expected, result)

    def test_2(self):
        config = PluginConfig('pyetl', 'pcaudit', ConfigTextLoader)
        ctx = ExecContext.from_dict(config.load(self.full_data))
        result = ctx["opsi"]
        expected = {
            'username': 'foo',
            'password': 'bar'
        }
        self.assertDictEqual(expected, result)

    @skip
    def test_3(self):
        config = PluginConfig('pyetl', 'pcaudit', ConfigTextLoader)
        ctx = ExecContext.from_dict(config.load(self.full_data))
        with self.assertRaises(KeyError):
            _ = ctx["unknown"]

    @skip
    def test_4(self):
        config = PluginConfig('pyetl', 'pcaudit', ConfigTextLoader)
        ctx = ExecContext.from_dict(config.load(self.full_data))
        with self.assertRaises(TypeError):
            _ = ctx["opsi.username.wrong"]

    def test_5(self):
        config = PluginConfig('pyetl', 'pcaudit', ConfigTextLoader)

        ctx = ExecContext.from_dict(config.load(self.full_data))
        result = ctx.itop.version
        self.assertEqual('1.3', result)

    def test_6(self):
        config = PluginConfig('pyetl', 'pcaudit', ConfigPackageLoader)
        config = config.load(package_name='tests.fixtures')
        ctx = ExecContext.from_dict(config)
        result = ctx.itop.version
        self.assertEqual('1.3', result)


class TestExtendedExecContext(TestCase):
    def setUp(self) -> None:
        self.ctx = ExecContext()
        self.ctx['level1'] = {'level2': {'value': 42}}

    def test_getitem_with_errors(self):
        with self.assertRaises(KeyError):
            _ = self.ctx.level1.value

    def test_find_with_errors(self):
        with self.assertRaises(KeyError):
            _ = self.ctx['level1.value']

        self.ctx['level1']['value'] = 'foo'
        with self.assertRaises(KeyError):
            _ = self.ctx['level1.value.val']


if __name__ == '__main__':
    run_tests(verbosity=2)

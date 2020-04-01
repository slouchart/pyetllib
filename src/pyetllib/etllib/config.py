from abc import abstractmethod

import importlib
import io
import pathlib
import os

import toml


class ConfigFileFinder:
    def __init__(self, app_name, paths=(), package_name=None):
        self.package_name = package_name
        self.paths = [pathlib.Path(path) for path in paths]
        self.paths += [
            pathlib.Path.cwd(),
            pathlib.Path("~").expanduser(),
        ]
        if os.name == 'posix':
            self.paths += [
                pathlib.Path('/etc', app_name)
            ]
        elif os.name == 'nt':
            self.paths += [
                pathlib.Path("~", 'AppData', 'Local', app_name).expanduser(),
                pathlib.Path("~", 'AppData', 'Roaming', app_name).expanduser(),
            ]

    def find_first(self, filename):
        for path in self.paths:
            if path.joinpath(filename).exists() \
                    and path.joinpath(filename).is_file():
                full_path_config = path.joinpath(filename)
                break
        else:
            paths = "\n".join(str(p) for p in self.paths)
            raise FileNotFoundError(
                f'No file named \'{filename}\' can be located '
                f'at these locations:\n'
                f'{paths}'
            )
        return full_path_config

    def find_from_package(self, filename):
        module = importlib.import_module(self.package_name)
        full_path_config = pathlib.Path(module.__file__).parent / filename
        return full_path_config


class ConfigLoader:
    def __init__(self, app_name, *args, **kwargs):
        self.app_name = app_name

    @abstractmethod
    def load(self):  # pragma: no cover
        pass


class ConfigPackageLoader(ConfigLoader):
    def __init__(self, app_name, package_name):
        super().__init__(app_name)
        self._finder = ConfigFileFinder(self.app_name,
                                        package_name=package_name)

    def load(self):
        filename = f"{self.app_name}.config.toml"
        full_path = self._finder.find_from_package(filename)
        with io.open(full_path, mode='r', encoding='utf-8') as f:
            return toml.load(f)


class ConfigFileLoader(ConfigLoader):
    def __init__(self, app_name, *args, **kwargs):
        super().__init__(app_name)
        self._finder = ConfigFileFinder(self.app_name, *args, **kwargs)

    def load(self):
        filename = f"{self.app_name}.config.toml"
        full_path = self._finder.find_first(filename)
        with io.open(full_path, mode='r', encoding='utf-8') as f:
            return toml.load(f)


class ConfigTextLoader(ConfigLoader):
    def __init__(self, app_name, text):
        super().__init__(app_name)
        self._text = text

    def load(self):
        return toml.loads(self._text)


class PluginConfig:

    def __init__(self, app_name, plugin_name, loader_factory):
        self.app_name = app_name
        self.plugin_name = plugin_name
        self.loader_factory = loader_factory

    def load(self, *args, **kwargs):
        loader = self.loader_factory(self.app_name, *args, **kwargs)
        return self._check_config(loader.load())

    def _check_config(self, config):
        result = {}
        if self.app_name not in config:
            raise RuntimeError(
                f"Invalid structure of the configuration "
                f"file for application {self.app_name}: "
                f"no section [{self.app_name}]"
            )
        else:
            result.update(config[self.app_name])
        if 'plugins' not in config \
                or self.plugin_name not in config['plugins']:
            raise RuntimeError(
                f"Invalid structure of the configuration file "
                f"for application {self.app_name}: no section [plugins] or "
                f"plugin's section [plugins.{self.plugin_name}]"
            )
        else:
            result.update(config['plugins'][self.plugin_name])

        return result

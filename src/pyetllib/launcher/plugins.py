__all__ = [
    'PluginGroup',
    'PluginRegistry',
    'MissingPlugin',
    'BrokenPlugin',
]


from pkg_resources import iter_entry_points
from weakref import WeakValueDictionary
import click
import importlib


class PluginRegistry:
    """ A stateless wrapper-adapter to load `click.Command` objects
    from a list of `pkg_resources.EntryPoints`
    The registry itself is maintained by `setuptools`as part
    of the distribution/installation process
    """
    _registries = WeakValueDictionary()

    @classmethod
    def instance(cls, plugins_group_name):
        if plugins_group_name in PluginRegistry._registries:
            return PluginRegistry._registries[plugins_group_name]

        if cls is not PluginRegistry:
            cls.plugins_group_name = plugins_group_name
            obj = cls()  # create a strong reference

            cls._registries[plugins_group_name] = obj
            assert PluginRegistry.validate_register(obj)
        else:
            obj = cls()  # create a strong reference
            obj.plugins_group_name = plugins_group_name
            cls._registries[plugins_group_name] = obj
            PluginRegistry.validate_register(obj)

        return obj

    def __del__(self):
        if hasattr(self, 'plugins_group_name') \
                and self.plugins_group_name in PluginRegistry._registries:
            del PluginRegistry._registries[self.plugins_group_name]

    @classmethod
    def reset_registries(cls):
        cls._registries = WeakValueDictionary()

    @classmethod
    def exists(cls, register_name):
        return register_name in PluginRegistry._registries

    @staticmethod
    def validate_register(registry):
        if not hasattr(registry, 'plugins_group_name'):
            raise RuntimeError("expected instance variable "
                               "'plugins_group_name' not found.")

        if registry.plugins_group_name is None \
                or len(registry.plugins_group_name) == 0:
            raise RuntimeError("instance variable 'plugins_group_name' "
                               "is None or empty.")

        assert registry.plugins_group_name in PluginRegistry._registries, \
            f"plugin group {registry.plugins_group_name} is not registered."

        return True

    def __iter__(self):
        return iter(self.get_plugins_list())

    def get_plugins_list(self):
        """Returns a list containing the names of all installed plugins.
        """
        return sorted([ep.name for ep in self.iter_plugins()])

    def iter_plugins(self):
        """Returns an iterator over the installed plugins
        as `pkg_resources.EntryPoint` instances.
        """
        return iter_entry_points(self.plugins_group_name)

    def find_plugin_by_name(self, name):
        """Returns the plugin named by `name`
        as an entry point from `[rectl_plugins]`.
        """
        for ep in iter_entry_points(self.plugins_group_name, name=name):
            pg = ep
            break
        else:
            pg = None
        return pg

    def __getitem__(self, name):
        item = self.find_plugin_by_name(name)
        if item:
            return item
        else:
            raise KeyError(name)

    def load_command_from_plugin(self, name, plugin=None):
        """Loads a `click.Command` from the plugin module and returns it.
        """
        plugin = plugin or self.find_plugin_by_name(name)
        if plugin is not None:
            try:
                module = importlib.import_module(plugin.module_name)
                command = getattr(module, plugin.attrs[0])
            except (ImportError, ValueError, IndexError, AttributeError) as e:
                command = BrokenPlugin(name, reason=str(e))

        else:
            return MissingPlugin(name)

        if command and isinstance(command, click.Command):
            return command
        else:
            return BrokenPlugin(name, reason=f'plugin {name} is not '
                                             f'an instance of `click.Command`')


class MissingPlugin(click.Command):
    """Useful class to avoid dealing with exceptions
     in case of a missing or misspelled plugin
    """

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.help = f"\nWarning: entry point '{self.name}' " \
                    f"could not be loaded. " \
                    f"Check your pyetllib ETL installation.\n"
        self.short_help = "Warning: could not load plugin."

    def invoke(self, ctx):
        click.echo(self.help, err=True, color=ctx.color)
        ctx.exit(2)


class BrokenPlugin(MissingPlugin):
    """Same as MissingPlugin but silently warns that a plugin is broken
    """

    def __init__(self, name, reason=None, **kwargs):
        super().__init__(name, **kwargs)
        self.reason = reason or 'Unknown reason'

    def invoke(self, ctx):
        click.echo(self.help, err=True, color=ctx.color)
        click.echo(f'Reason: {self.reason}', err=True, color=ctx.color)
        ctx.exit(1)


class PluginGroup(click.MultiCommand):
    """Specific instance of `click.MultiCommand`
    that deals with registered plugin modules containing subcommands
    """

    def __init__(self, *args, plugin_group_name=None, **kwargs):
        self.plugin_group_name = plugin_group_name
        super().__init__(*args, **kwargs)
        pass

    def list_commands(self, ctx):
        return PluginRegistry.instance(
            self.plugin_group_name
        ).get_plugins_list()

    def get_command(self, ctx, name):
        return PluginRegistry.instance(
            self.plugin_group_name
        ).load_command_from_plugin(name)

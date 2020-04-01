import click

from .plugins import PluginGroup, PluginRegistry


@click.group()
def pyetl():
    """A utility script to run ETL jobs as plugins"""
    pass


@pyetl.group()
def show():
    """Displays ETL configuration, plugins and jobs"""
    pass


@show.command()
def plugins():
    """Displays installed ETL plugins"""
    plugins = PluginRegistry.instance('pyetl_plugins').get_plugins_list()
    if plugins:
        click.echo('\n'.join(plugins))
    else:
        click.echo('No plugin installed')


@pyetl.command(cls=PluginGroup,
               plugin_group_name='pyetl_plugins',
               options_metavar='[global options]',
               subcommand_metavar='<ETL plugin> [plugin options]',
               epilog="To display a list of installed plugins, "
                      "please execute:"
                      " \n\n    pyetl show plugins")
def run(*_):
    """Runs an ETL job as a plugin"""
    pass

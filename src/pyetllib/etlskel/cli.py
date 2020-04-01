
"""
Usage: etlskel [OPTIONS] <project name>

Options:

  --template-dir / --no-template-dir

  Creates a package for Jinja2 template files under the main package

  -p, --package-name <name>

  Specifies a different name for the main package

  -s, --source_dir

  Collates all sources under a 'src' directory

  -T, --no-test-package

  Skips the creation of the unit testing package

  --help

  Show this message and exit.

  Examples:


"""

import click
import sys
import os

from .operations import create_skeleton


@click.command()
@click.option('--template-dir/--no-template-dir', default=True,
              help="Creates a package for Jinja2 template files "
                   "under the main package")
@click.option('-p', '--package-name', metavar='<name>', type=str,
              help="Specifies a different name for the main package")
@click.option('-s', '--source-dir', is_flag=True, default=False,
              help="Collates all sources under a 'src' directory")
@click.option('-T', '--no-test-package', is_flag=True, default=False,
              help="Skips the creation of the unit testing package")
@click.option('-b', '--bare', is_flag=True, default=False,
              help="Creates a bare project without tox/git init files")
@click.argument('project_name', type=str, metavar='<project name>')
def etlskel(project_name, package_name=None, template_dir=True,
            source_dir=False, no_test_package=False, bare=False):

    cmd, what_to_do = create_skeleton(project_name,
                                      main_package_name=package_name,
                                      create_template_dir=template_dir,
                                      create_source_dir=source_dir,
                                      no_test_package=no_test_package,
                                      bare=bare)
    click.echo("The following files/directories are going to be created:")
    click.echo(what_to_do)
    result = click.prompt('Do you confirm?', default='n',
                          type=click.Choice(('Y', 'n'), case_sensitive=False))
    if result.lower() == 'y':
        cmd.do()
        if cmd.failed:  # pragma: no cover
            click.echo(cmd.failure, err=True)
            sys.exit(1)
        else:
            click.echo(f"Structure of project {project_name} "
                       f"successfully created in {os.getcwd()}")
    sys.exit(0)

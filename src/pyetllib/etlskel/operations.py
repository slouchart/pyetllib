__all__ = [
    'create_skeleton'
]

import io
from pathlib import Path
from jinja2.exceptions import TemplateError
from ..etllib.utils.j2 import load_template_from_pkg
from ..etllib.tools.j2 import render_template
from ..etllib.commands import CreateDir, CreateTextFile


class InitPackage(CreateDir):
    def __init__(self, package_name, root_path, *args, **kwargs):
        self.package_name = package_name
        self.root_path = root_path

        package_path = Path(root_path).joinpath(package_name)
        super().__init__(package_path)

        self.add_subcommand(CreateTextFile, '__init__.py', package_path)


def create_skeleton(project_name,
                    main_package_name=None,
                    create_template_dir=True,
                    create_source_dir=False,
                    no_test_package=False,
                    bare=False):

    main_package_name = main_package_name or project_name
    project_root_dir = Path.cwd()
    project_dir = project_root_dir.joinpath(project_name)

    root = CreateDir(project_dir)

    s = io.StringIO()

    def what_to_do(cmd):
        s.writelines(str(cmd.path) + "\n")

    if create_source_dir:
        source_dir = project_dir.joinpath('src')
        root.add_subcommand(CreateDir, source_dir)
    else:
        source_dir = project_dir

    main_package_dir = source_dir.joinpath(main_package_name)

    pkg_cmd = root.add_subcommand(InitPackage, main_package_name, source_dir,
                                  name='create package dir')

    if create_template_dir:
        pkg_cmd.add_subcommand(InitPackage, 'templates', main_package_dir,
                               name='create templates package dir')
        if create_source_dir:
            content = 'include src/*/templates/*.j2'
        else:
            content = 'include */templates/*.j2'
        root.add_subcommand(CreateTextFile, 'MANIFEST.in', project_dir,
                            content=content)

    for filename in ('extract', 'transform', 'publish'):
        pkg_cmd.add_subcommand(CreateTextFile, f'{filename}.py',
                               main_package_dir)

    if not no_test_package:
        root.add_subcommand(InitPackage, 'tests', project_dir,
                            name='create test package')

    root.add_subcommand(CreateTextFile, 'README.md', project_dir,
                        name='create README.md')

    template_package = f"{main_package_name}.templates"
    data = {
        'project_name': project_name,
        'template_package': template_package if create_template_dir else None,
        'entry_point': main_package_name,
        'package': f'{main_package_name}.cli',
        'function': main_package_name,
        'has_source_dir': create_source_dir,
        'no_test_package': no_test_package
    }
    content = ''
    try:
        template = load_template_from_pkg('recetl.etlskel', 'setuppy.j2')
        content = render_template(template, **data)
    except TemplateError:  # pragma: no cover
        pass
    root.add_subcommand(CreateTextFile, 'setup.py', project_dir,
                        name='Create setup.py', content=content)

    content = ''
    try:
        template = load_template_from_pkg('recetl.etlskel', 'cli.j2')
        content = render_template(template, function=main_package_name,
                                  package=project_name)
    except TemplateError:  # pragma: no cover
        pass
    pkg_cmd.add_subcommand(CreateTextFile, 'cli.py', main_package_dir,
                           name='create cli.py', content=content)

    if not bare:
        content = ''
        try:
            template = load_template_from_pkg('recetl.etlskel', 'toxini.j2')
            content = render_template(
                template,
                has_source_dir=create_source_dir,
                package_name=main_package_name
            )
        except TemplateError:  # pragma: no cover
            pass
        root.add_subcommand(CreateTextFile, 'tox.ini', project_dir,
                            name='create tox.ini', content=content)

        content = ''
        try:
            template = load_template_from_pkg('recetl.etlskel', 'gitignore.j2')
            content = render_template(template)
        except TemplateError:  # pragma: no cover
            pass
        root.add_subcommand(CreateTextFile, '.gitignore', project_dir,
                            name='create .gitignore', content=content)

    root.visit(what_to_do)
    return root, s.getvalue()

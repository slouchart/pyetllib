# -*- coding:utf-8 -*-

__all__ = [
    'load_template_from_pkg',
    'load_template_from_path',
    'get_templates_path',
    'load_template',
]


from pathlib import Path
import jinja2 as j2


def load_template_from_pkg(pkg_name, template_name):
    try:
        return j2.Environment(
            loader=j2.PackageLoader(pkg_name)
        ).get_template(template_name)
    except (ModuleNotFoundError, KeyError) as e:
        raise j2.TemplateError(message=str(e))
    except j2.TemplateNotFound as e:
        raise j2.TemplateError(message=f"Template not found '{str(e)}'")


def load_template_from_path(path_name, template_name):
    try:
        template_path = get_templates_path(start_at=path_name)
        if not Path(template_path).exists():
            raise j2.TemplateError(
                f"Template path '{template_path}' does not exist"
            )
        return load_template(
            template_path,
            template_name
        )
    except j2.TemplateNotFound as e:
        raise j2.TemplateError(message=f"Template not found '{str(e)}'")


def get_templates_path(template_folder_name='templates', path_parts=(),
                       start_at=None):
    """ Returns the path of the 'templates' folder under the module root
    """
    start_at = start_at or Path(__file__).parent.parent.parent
    path_parts = path_parts + (template_folder_name,)
    return Path(start_at).joinpath(*path_parts)


def load_template(template_path, template_name):
    """Loads a Jinja template from a given path and name

    Arguments:
        template_file {PathToDir: Path/String}
        template_name {Filename: String}

    Raises:
        IOError: This path does not exist
    """
    if isinstance(template_path, Path):
        template_path = str(template_path)

    file_loader = j2.FileSystemLoader(template_path)
    env = j2.Environment(loader=file_loader, trim_blocks=True,
                         lstrip_blocks=True)
    return env.get_template(template_name)

def render_template(template, streaming=False, **data):
    """Render data according to a Jinja template to a given stream

    Arguments:
        template {Jinja2 Template}
        streaming {bool}
        data {Iterable}

    Returns:
        {String}

    Raises:

    """
    if streaming:
        return template.stream(**data)
    else:
        return template.render(**data)

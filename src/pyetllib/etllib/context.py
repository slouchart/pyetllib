# -*- coding:utf-8 -*-

__all__ = [
    'create_exec_context',
    'ExecContext'
]


import re
from functools import partial


def create_exec_context(**ctx):
    return ExecContext.from_params(**ctx)


class ExecContext(dict):
    """
    Defines a Context class specifically designed to be used by functions
    declared in sibling modules `extract`, `transform`, `publish` or `load`
    """
    def __init__(self, *args, **kwargs):
        super(ExecContext, self).__init__(*args, **kwargs)

    def __getattr__(self, item):
        m = re.match(r'^set_(?P<property>\w+)$', item)
        if m:
            attr = partial(super(ExecContext, self).__setitem__,
                           m.group('property'))
        else:
            attr = super(ExecContext, self).__getitem__(item)

        if isinstance(attr, dict):
            attr = ExecContext.from_dict(attr)
        return attr

    def __getitem__(self, item):
        return self._find(item)

    def has_property(self, item):
        return super(ExecContext, self).__contains__(item)

    @classmethod
    def from_dict(cls, ctx):
        return ExecContext(ctx.items())

    @classmethod
    def from_params(cls, **ctx):
        return cls.from_dict(ctx)

    def _find(self, key):
        keys = key.split('.')
        target = self

        while len(keys):
            key = keys.pop(0)
            try:
                target = dict(target)[key]
                if isinstance(target, dict) and len(keys):
                    target = ExecContext.from_params(**target)
                elif len(keys) == 0:
                    continue
                else:
                    raise KeyError(key)
            except KeyError:
                raise

        return target

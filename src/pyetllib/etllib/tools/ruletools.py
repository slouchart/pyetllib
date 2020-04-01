import re
from toolz import complement
from functools import wraps, partial
from .fieldtools import fextract
from .streamtools import pipable


def set_field(default):
    def decorator(func=None):
        decorator.__partial_decorator__ = False
        if func is not None:
            @wraps(func)
            def inner(value, others, *args, **kwargs):
                value = func(value, others, *args, **kwargs)
                return default if value is None else value

            inner.__all_values__ = True

        else:
            def inner(*_):
                return default

            inner.__all_values__ = False

        return inner

    decorator.__partial_decorator__ = True
    return decorator


def default_if_equal(value, default):
    """Implements the rule: default if v == value else v"""
    return default_if_false(lambda v: v != value, default)


def default_if_false(predicate, default):
    """Implements the rule: v if v else default"""
    def decorator(func=lambda x: x):
        decorator.__partial_decorator__ = False
        @wraps(func)
        def inner(v):
            if predicate(v):
                return func(v)
            else:
                return default

        inner.__all_values__ = False
        return inner
    decorator.__partial_decorator__ = True
    return decorator


def default_if_match(pattern, default):
    """Implements the rule: default if v match pattern else v"""
    return default_if_true(lambda v: re.match(pattern, v), default)


def default_if_not_equal(value, default):
    """Implements the rule: default if v != value else v"""
    return default_if_false(lambda v: v == value, default)


def default_if_no_match(pattern, default):
    """Implements the rule: v if v match pattern else default"""
    return default_if_false(lambda v: re.match(pattern, v), default)


def default_if_none(default):
    """Implements the rule: default if v is None else v"""
    return default_if_true(lambda v: v is None, default)


def default_if_true(predicate, default):
    """Implements the rule: default if v else v"""
    predicate = complement(predicate)
    return default_if_false(predicate, default)


class mapping_rule:
    """Creates an association between a field name and a function
    and applies these rules to a data dictionary
    Usage:
    >>> rule = mapping_rule('foo', str.lower)
    >>> mapping_rule.apply([rule], {'foo': 'BAR'}
    { 'foo': 'bar'}
    """
    def __init__(self, field_name, func, provide_all_values=False):
        """`field_name` may be of any type suitable for a dictionary key
        `func` must be a callable that accepts a single argument and returns
        a value"""
        self.field_name = field_name
        if hasattr(func, '__partial_decorator__') \
                and getattr(func, '__partial_decorator__'):
            self.func = func()
        else:
            self.func = func
        if hasattr(self.func, '__all_values__'):
            self.provide_all_values = self.func.__all_values__
        else:
            self.provide_all_values = provide_all_values

    def __call__(self, ddict):
        if self.field_name in ddict:
            k, v = self.field_name, ddict[self.field_name]
        else:
            k, v = self.field_name, None

        if self.provide_all_values:
            return k, self.func(v, tuple(ddict.items()))
        else:
            return k, self.func(v)

    @classmethod
    def apply(cls, rules, ddict):
        """Applies each rule in rules to the data dictionary and returns
        the result"""
        involved_keys = set(r.field_name for r in rules)
        remaining_keys = set(ddict.keys()) - involved_keys
        result = fextract(remaining_keys, ddict)
        result.update(
            dict(
                map(
                    lambda rule: rule(ddict),
                    rules
                )
            )
        )
        return result

    @classmethod
    def get_apply_func(cls, rules):
        return pipable(partial(cls.apply, rules))

# flake8: noqa
from .streamtools import (
    aggregate,
    filtertruefalse,
    groupby,
    lookup,
    reduce,
    replicate,
    select,
    stream_converter,
    stream_generator,
)

from .streamtools import (
    compose,
    call_next,
    mcompose,
    pipable,
    pipeline,
    pipe_data_through,
    call_next_starred,
    xargs,
)

from .fieldtools import (
    fextract,
    flookup,
    fremove,
    frename,
    freverse_lookup,
    fmap,
    fsplit,
)

from .ruletools import (
    default_if_equal,
    default_if_not_equal,
    default_if_false,
    default_if_true,
    default_if_match,
    default_if_no_match,
    default_if_none,
    mapping_rule,
    set_field,
)

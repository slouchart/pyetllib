def filter_reject(predicate, iterable, use_tee=False):  # pragma: no cover
    """Sort out elements for `iterable` depending on the outcome
    of `predicate`. If `predicate` returns `True`, the element
    is considered rejected otherwise it is accepted.

    Returns two iterables as a tuple, the first being the accepted
    list and the second being the rejected list.

    `predicate` must be a `callable` that accepts a single argument and
    returns a `bool`

    The `use_tee` optional flag tells the function about which approach to use
    when duplicating the input iterable. When `use_tee` is set to `True`, the
    function calls `itertools.tee` which may lead to requiring significant
    auxiliary storage. For most cases, setting `use_tee` to `False` is just
    fine.
    """
    raise DeprecationWarning

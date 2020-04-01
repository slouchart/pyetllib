# `etllib.tools` — data transformation functions
---


## Glossary

> **currying**:
a technique to translate the evaluation of a function that takes
multiple arguments to the evaluation of a sequence of functions, each
of these taking one single argument

> **data**:
an item of information

> **data dictionary**:
a `data` item with a `dict`-like interface. May be either a built-in
`dict` or a named tuple from `collections.namedtuple`

> **data stream**: 
an iterable comprised of `data` items

> **field**:
a key of a data dictionary

> **higher-order function**:
a function that accepts another function as its main argument 
and/or returns a function

> **I/O stream**:
an output object with a `write` method akin to `io.TestIOBase`

> **predicate**:
a function that accepts a single argument and returns `True` or `False`
based on the value of its argument.

## Fields functions

### function `fextract(keys, data_dict)`
Returns a **data dictionary** made from `key, value` pairs from `data_dict`
with each `key` value appears in `keys`.
``` python
>>> fextract(('foo', ), {'foo': 42, 'spam': None})
{'foo': 42}
``` 
### function `flookup(lookup_map, keys, data_dict)`
Returns a **data dictionary** with the same key structure as `data_dict`
 but with all values keyed by each `keys` taken from values in 
 `lookup_map`.
``` python
>>> flookup({42: 'bar'}, ('foo', ), {'foo': 42, 'spam': None})
{'foo': 'bar', 'spam': None}
```

### function `fmap(keys, funcs, data_dict, val_as_args=False)`
Returns a **data dictionary** with the same key structure as `data_dict`
but with all values keyed by each `keys` transformed by a function
from `func` at the same index. 
``` python
>>> data = {'foo': 'niiiiii!', 'bar': None}
>>> fmap(('foo', 'bar'), (str.upper, lambda x: 42), data)
{'foo': 'NIIIIII!', 'bar': 42}
```

The optional argument `val_as_args` when 
set to `True` allows a `func` to be called with a variable number of
arguments. These arguments are set using the operator `*` on the value
returned by `data_dict`.
``` python
>>> data = {'foo': (3, 4), 'bar': 9}
>>> fmap(('foo', ), (operator.add, ), data, True
{'foo': 7, 'bar': 9}
```

### function `fremove(keys, data_dict)`
Returns a **data dictionary** with all the `key, value` pairs from
`data_dict` except the ones keyed by any key contained in `keys`.
``` python
>>> fremove(('spam', ), {'foo': 42, 'spam': None})
{'foo': 42}
```

### function `frename(keys, data_dict)`
Returns a **data dictionary** with some keys renamed using a provided
`keys` mapping. The new key names are the values of `keys` keyed by
their old names.
``` python
>>> frename({'spam': 'bar'}, {'foo': 42, 'spam': 0})
{'foo': 42, 'bar': 0}
```

### function `freverse_lookup(lookup_map, keys, data_dict)`
Returns a **data dictionary** with the same key structure as 
`data_dict`. Key values in `keys` are translated using the contents of
`lookup_map` in the following way: if a value from `data_dict` appears 
in a value from `lookup_map`, the value from `data_dict` is replaced 
by the **key** from `lookup_map`.

`lookup_map` must be a `dict`-like object of collections keyed by any
hashable type. 

``` python
>>> data = {'spam': 666}
>>> freverse_lookup({'foo': (42, 0, 666)}, ('foo', ), data)
{'foo': 'spam'}
```


### function `fsplit(keys, data_dict)`
Returns two **data dictionary** as a tuple. The first returned data
dictionary contains values from `data_dict` keyed by the contents 
of `keys` (a collection of keys). The second data dictionary contains
all the remaining keys.
``` python
>>> fsplit(('spam', ), {'foo': 42, 'spam': 0})
({'spam: 0'}, {'foo': 42})
```

## Curryfied field functions
All the preceding functions are available in a curryfied version in the
namespace `pyetllib.etllib.curried`.

## Streams and data functions
### function `aggregate(aggregator, groupings)`
Applies the function `aggregator` to an iterable of keyed-groups 
provided through the `grouping` argument and most often built with 
the `groupby` function described below.

### function `filtertruefalse(predicate, iterable)`
Returns two iterables, the first one containing all items from
`iterable` for
which `predicate`is `True`, the second one containing of course, all
the elements for which `predicate` evaluates to `False`. THe function
expects the argument `predicate` to be a callable accepting a single
argument whose type is compatible with the content of `iterable` and
returning a `bool`.

### function `groupby(key, iterable)`
Returns all elements from `iterable` grouped by a common value called
the *key*. The 
argument `key` is a function that maps an element to this key. The 
return value itself is an iterable of `groupings` that are `tuple`-like
objects associating an iterator of elements with their key.

This function differs from `itertools.groupby` by its signature which
has been made compatible with `functools.partial` for currying.

### function `join(*iterables, fill_value=None)`
Produces an iterable of tuples built from elements from the 
`iterables` passed as arguments. Each item of such a tuple is drawn
from the iterable with the same position in the argument line. If an
iterable cannot provide a value, the value of `fill_value`is used.

### function `lookup(iterable, key=lambda x: x, lookup_map=None, merge=False, enable_rejects=False)`

Filters from `iterable` all its elements that have a matching in 
a `dict`-like object provided through the `lookup_map` argument. 
The `key` argument is a callable used by `lookup` to extract a key 
value from an element and defaults to the identity function. 
The `merge` argument may be either a `bool` or a `callable`. If 
`merge` is `False`, elements from `iterable` are returned as is. If
`merge` is set to `True`, the returned elements are tuples associating
an element from `iterable` with the matching value from `lookup_map`.
If `merge` is a callable, it must accept two arguments and return a 
value. The parameter `enable_rejects`, if set to `True` allows the
function to return a second iterator containing all elements from 
`iterable` for which no matching could not be found.

### function `pipe_data_through(data, *steps)`
Left-composes a function from the `steps` arguments and applies it
to `data`. All the `steps` must share the same signature and returns
a value compatible with this signature.

Roughly equivalent to:
``` python
def pipe_data_through(data, *steps):
    def left_compose(a, b):
        return lambda v: b(a(v))
        
    pipeline = reduce(left_compose, steps)
    return pipeline(data)
```

### function `reduce(function, iterable, initial=None)`

Wraps `functools.reduce` by providing `initial` as an actual
keyword parameter to better fit partial evalutation with
`functools.partial`

### function `replicate(iterable, n=2)`

With equivalent semantics to `itertools.tee`, this function provides
a **non thread-safe** but more efficient way to duplicate an iterable.

### function `select(predicates, iterable, strict=False)`

This function forks `iterable` into as many iterators as the number
of elements in `predicates` **plus one** and returns them as a `tuple`. 
Each of these iterators contains
elements from `iterable`for which the predicate that shares the same 
index position returns `True`. 

The last iterator is the "default"
iterator that yields elements for which all the predicates are `False`.

If `strict` is set to `False`, an element might be shared between 
different iterators if their associated predicates all yield `True` for
this element. If `strict` is set to `False`, each element is guaranteed
to figure in one and only in one output iterator.

### function `split(func, iterable, expected_length=-1)`

Transforms each element from `iterable` into parts according to
the return value of `func`. Each of these parts are then sent to a
different iterator. The function returns a tuple containing all these 
iterators.

If `expected_length` is a positive integer, the function initializes
its return value with as many iterators. During iteration, if the 
function encounters an item that is split in more parts than the
number of iterators, an error is raised. If `expected_length` is 
not a positive integer, the number of output iterators is computed
from the first element of `iterable`. In that case, if `func` yields
no part, the function returns an empty tuple.

### function `stream_converter(from_, to_, *args, **kwargs)`

Returns a function able to convert an instance 
of type `from_` to an instance of type `to_`. Converters are provided 
for the following pairs of types:

* `tuple` → `str`-keyed `dict`, a list of `keys` must be passed 
as an argument and the optional parameter `key_type` must be set 
to `str`
* `tuple` → `int`-keyed `dict`, the optional parameter `key_type` 
must be set to `int`
* `dict` → `tuple`
* `str`-keyed `dict` → `collection.namedtuple`
* `tuple` → `collections.namedtuple`, a list of `keys` must be passed as
an argument.

### decorator function `stream_converter.dispatch(from_, to_, key_type=None)`
Decorates a function to register it as a stream converter. The 
decorated function should provide in its signature all necessary 
arguments and parameters for a call to 
`stream_converter(from_, to_, *args, **kwargs)`

### function `stream_generator(keys, funcs, nb_items)`

Returns a `generator` that yields as many data dictionaries as the 
value of `nb_items`. Each data dictionary is built from the provided
`keys` as a schema and its values are provided by calls to each
element of `funcs` which can also be generators. If `nb_items` is 
negative, the generator yields as long as `funcs` can provide values.

## Higher-order functions

### function `call_next(iterable)`

Encapsulates `iterable` as an iterator and returns a callable closure
that yields the returned value of this iterator `next` on each call.

### function `call_next_starred(*items)`

The variadic version of `call_next`

### function `compose(*funcs)`

Right-composes its arguments into a single function. For instance, 
`compose(f, g)(a)` is equivalent to `f(g(a))`. 

Works only for monadic functions.

### function `mcompose(*funcs)`

Right-composes variadic functions passed as arguments. 

### decorator function `pipable(callable_)`

Decorates any callable to be used with the syntactic sugar operator `|`
for left composition. For instance, `(pipable(f) | pipable(g))(a)` is 
equivalent to `g(f(a))`

### function `pipeline(*funcs)`

Left-composes monadic functions passed as arguments. `pipeline(f, g)(a)`
is equivalent to `g(f(a))`

### function `xargs(g, funcs, as_iterable=False)`

Returns a function that accepts a tuple as an arguments and then
maps each element of this tuple to one of the `funcs` generating another
tuple in the process. 
Finally, the function `g` is called with the tuple elements as arguments.
If this tuple does not contain enough elements to map all the `funcs`,
the last element is repeated to provide an argument to the remaining 
functions.
`funcs` must be a non-empty sequence of callables. `g` should be 
a variadic callable. Set `is_iterable` to `True` if `g` is monadic.


## Rules

### class `mapping_rule`
`mapping_rule(field_name, func, provide_all_values=False)` 
initializes an instance of  `mapping_rule` targeting a data 
dictionary key called `field_name` and setting it with the value
returned from `func`. `func` is called a **valuation method** and must 
be a callable accepting either one
argument or two arguments, in this case, `provide_all_values` must be
set to `True`.

#### methods
`apply(cls, rules, ddict)` executes all the instances of `mapping_rules`
found in `rules` to the data dictionary `ddict` and returns the result.

`get_apply_func(cls, rules)` is a function factory that returns a 
`pipable` partial of `mapping_rule.apply`.

## Rule definition helpers

### function decorator `set_field(default)`
Decorates a function to adapt it to being used as a rule valuation 
method. If the decorated function returns `None` the value provided by
`default`is used instead.

### function `default_if_none(default)`
Returns a rule valuation method that returns `default` if its argument
is `None`.

### function `default_if_false(predicate, default)`
Returns a rule valuation method that returns `default` if
`predicate(v)` evaluates to `False`.

### function `default_if_true(predicate, default)`
Returns a rule valuation method that returns `default` if
`predicate(v)` evaluates to `True`.

### function `default_if_equal(value, default)`
Returns a rule valuation method that returns `default` if
its argument equals to `value`.

### function `default_if_not_equal(value, default)`
Returns a rule valuation method that returns `default` if
its argument differs from `value`.

### function `default_if_match(pattern, default)`
Returns a rule valuation method that returns `default` if
its argument matches `pattern`.

### function `default_if_no_match(pattern, default)`
Returns a rule valuation method that returns `default` if
its argument does not match `pattern`.
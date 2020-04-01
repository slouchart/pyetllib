# `etllib` — ETL toolkit

--- 
This packages offers classes and functions that eases the process of 
creating and customizing data manipulation pipelines in Python.

## Main features
* Functional style programming
* Data iterators and dictionaries
* Jinja2 rendering — load and render your Jinja2 templates with ease
* Stream publishing — publish your data from an iterator to a stream
* `ExecContext` — a smart `dict` to hold execution parameters
* Timed statistics for ETL transformations — a decorator to log the 
elapsed execution time of your pipeline

## Basic usage

### Loading and rendering a template
Assuming there is a `templates` directory under your main package 
directory, it is easy to load any template from this directory.
``` python
>>> from pyetllib.etllib.j2 import load_template, get_templates_path
>>> template = load_template(get_templates_path(), 'my_template.j2')
```

Once the template is loaded, rendering it from data is piece of cake:
``` python
>>> from pyetllib.etllib.j2 import render_template
>>> content = render_template(template, **data)
```

### Defining an execution context
```python
>>> from pyetllib.etllib.context import create_exec_context
>>> ctx = create_exec_context()
>>> ctx.set_name('foo')
>>> print(ctx.name)
foo
```

### Publishing data through any I/O stream
```python
>>> iterators = (iter(range(5)),)

>>> from pyetllib.etllib.streams import publish_to_stream
>>> publish_to_stream(*iterators, record_converter=str)
0
1
2
3
4

>>> import io
>>> s = io.StringIO()
>>> publish_to_stream(*iterators, record_converter=str, record_delimiter=',', stream=s)
>>> print(s.getvalue())
0,1,2,3,4,
```

## Advanced usage

Beyond the use of built-in functions such as `map` or `filter`, dealing 
with data streams often involves more complex transformations. The
package `pyetl.etllib` provides a wide range of such functions. The 
few examples below illustrate somme common usage.

### Data streams and transformation functions

The `stream_generator`function can be used to build up a data stream
from different sources such as the `faker` module

``` python
>>> from pyetllib.etllib import stream_generator, call_next
>>> from faker import Faker
>>> from functools import partial
>>> from itertools import count
>>> fake = Faker()
>>> fields = ('id', 'name')
>>> funcs = (partial(call_next, count(start=1)), fake.name)
>>> gen = stream_generator(fields, funcs, nb_items=2)
>>> gen = list(gen)
>>> gen
[{'id': 1, 'name': 'Jessica Wilson'}, {'id': 2, 'name': 'Bradley Garcia'}]
```

The `stream_converter` function factory helps building converters
between data types to be used to turn, for example, a stream of `dict`
into a stream of `tuple`.

``` python
>>> from pyetlib.etllib import stream_converter
>>> converter = stream_converter(dict, tuple)
>>> gen = map(lambda d: converter(d)[1], gen)
>>> list(gen)
['Jessica Wilson', 'Bradley Garcia']
```

### Filtering data

The `filtertruefalse`function extends the semantics of built-in `filter`
to also return the part for which the `predicate`is `False`.

``` python
>>> from pyetllib.etllib import filtertruefalse
>>> data = list(range(5))
>>> odds, evens = filtertruefalse(lambda x: bool(x % 2), data)
```

### Modifying data dictionaries

The natural representation for a database row of a line from a tabular 
file is the built-in `dict` type. `pyetllib.etllib` provides a few
useful functions to transform such a `dict` into another :

* `fmap` to map functions to keys and produce a dict mapping
 the original keys to the functions' return values
* `fextract` to produce a `dict` using only a subset of the original 
keys
* `frename` to produce a `dict` with a new set of keys.

``` python
>>> data = [{'foo': 1, 'bar': 'jessica wilson'}, {'foo': 2, 'bar': 'bradley garcia'}]
>>> from pyetllib.etllib.curried import frename, fextract, fmap
>>> data = list(map(frename({'foo': 'id', 'bar': 'name'}), data))
>>> data = list(map(fmap(('name', ), (str.capitalize, )), data))
>>> data = list(map(fextract(('name', )), data))
>>> data
[{'name': 'Jessica Wilson'}, {'name': 'Bradley Garcia'}]
```

### Selecting, replicating, splitting, joining

The standard library does not contain a lot of functions able
to tee iterators except the aptly named `itertools.tee` which is 
thread-safe but may 
consume computing resources for large iterators. `recetl.etllib` 
proposes `replicate`, a replacement for `itertools.tee` that is 
not thread-safe but
consume lot less resources relying on lazy evaluation.

In addition, some other `tee`-like functions are available:

* `select` routes items according to a list of predicates like the 
if-then-elif-else statement
* `split` is a one-to-many association based on how the provided 
function slices each item for the input data stream
* `join` is the reverse operation of `split`, it takes several 
iterables, composes a tuple at each iteration and returns it in a single
iterable

``` python
>>> data = [{'id': 1, 'name': 'Jessica Wilson'}, {'id': 2, 'name': 'Bradley Garcia'}]
>>> from pyetllib.etllib import replicate, select, split, join
>>> src1, src2 = replicate(data, n=2)
>>> jessica, others = select((lambda d: d['name'] == 'Jessica Wilson'), src1)
>>> ids, names = split(lambda d: (d['id'], d['name']), src2, expected_length=2)
>>> list(join(ids, names))
[(1, 'Jessica Wilson'), (2, 'Bradley Garcia')]
```

### Lookups

The `lookup` function allows a `dict`-like object to be probed with
values from an iterable and returns a iterable of tuples each one
merging an item from the iterable and the matching value from the 
lookup map.

The lookup function is highly customizable as its caller may provide
a different key extraction strategy and a different merging strategy
or no merging at all.

``` python
>>> from pyetllib.etllib import lookup
>>> list(lookup(iter(range(5)), key=lambda n: n%2, lookup_map={0: 'even', 1: 'odd'}, merge=True))
[(0, 'even'), (1, 'odd'), (2, 'even'), (3, 'odd'), (4, 'even')]
```

### Rules

Rules provide a convenient way to build a data dictionary from another 
one when using functions like `fextract`, `frename` or `fmap` prove too 
clumsy.

A `mapping_rule` defines a strategy that applies to one and only 
one key. The actual strategy is provided by a function that accepts
the keyed-value and optionally all the other values of the data 
dictionary and must return a value. That value is set to be the value
of the returned data dictionary by any further call to `mapping_rule`.

`recetl.etllib` provides somme helpers to defines common rules like
setting a default value if a predicate is `False`.

``` python
>>> from pyetllib.etllib import mapping_rule
>>> data = {'a': 1, 'b': 2}
>>> def _add(_, t):
        d = dict(t)
        return d['a'] + d['b']

>>> rules = (mapping_rule('a+b', _add, provide_all_values=True),)
>>> mapping_rule.apply(rules, data)
{'a': 1, 'b': 2, 'a+b': 3}
```

### Pipelines and composers

With that many functions used to transform data streams, a program
written with `recetl.etllib` primitives can become really cumbersome
being a nested structure of calls to `map`/`filter` as shown below:
``` python
before = ...  # some iterable
after = map(
    fextract(...),
    map(
        fmap(...),
        map(
            frename(...),
            map(
                stream_converter(...)
                before
            )
        )
    )
)
```

A good way to increase the readability of such constructs is to compose
functions. `recetl.etllib` exposes three different approaches to 
composability :

* basic function composition with `compose` and `mcompose`
* data oriented pipelining with `pipe_data_through`
* function-oriented pipelining with `pipeline` and `pipable`:

``` python
from pyetllib.etllib import pipable
data_process = pipable(stream_converter(...)) \
    | pipable(frename(...)) \ 
    | pipable(fmap(...)) \
    | pipable(fextract(...))
    
after = map(data_process, before)

```





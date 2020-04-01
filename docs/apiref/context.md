# `etllib.context` — smart execution context
---

## function `create_exec_context(**ctx)`
Factory function that returns an instance of `ExecContext` from 
optional keyword parameters

## class ```ExecContext```
`ExecContext(*args, **kwargs)`
defines an ```ExecContext``` instance to be used by functions declared
in ETL script modules `extract`, `transform`, `publish` or `load`

### ancestors (in MRO)
* `builtins.dict`

### methods
`has_property(self, item)` returns `True` if the parent `dict` 
instance contains `item` as a key.

`from_dict(cls, ctx)` returns a new instance of `ExecContext` 
initialized from `ctx` which mist be a `dict`-like object.

`from_params(cls, **ctx)` returns a new instance of `ExecContext`
initialized from optional keyword parameters.

### properties
An instance of `ExecContext` may have any property once explicitly
defined :
```
>>> from pyetllib.etllib.context import ExecContext
>>> ctx = ExecContext()
>>> print(ctx.foo)
KeyError: 'foo'
>>> ctx.set_foo('spam')
>>> print(ctx.foo)
spam
```

Setting a property can be done using the special construct 
`set_<property>` or by accessing the context as a `dict`:
```
>>> from pyetllib.etllib.context import ExecContext
>>> ctx = ExecContext()
>>> ctx.set_foo('eggs')
>>> print(ctx.foo)
eggs
>>> ctx['foo'] = 'spam'
>>> print(ctx.foo)
spam
```

### sub-contexts and composite keys
An instance of `ExecContext` may contain other instances:
```
>>> from pyetllib.etllib.context import ExecContext
>>> ctx = ExecContext()
>>> ctx.set_foo({'spam': 42})
>>> ctx.foo
{'spam': 42}
>>> type(ctx.foo)
<class 'pyetllib.etllib.context.ExecContext'>
``` 

Access to a sequence of keys mapping `dict`-like object is also 
possible:
```
>>> from pyetllib.etllib.context import ExecContext
>>> ctx = ExecContext()
>>> ctx.set_foo({'spam': 42})
>>> ctx['foo.spam']
42
```
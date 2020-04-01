# `etllib.commands` - command pattern implementation

---

## class `Command`
`Command(*args, **kwargs)`
 is the base class implementing the Command pattern.
It supports undo and subcommands.
Subclass this class to create your own `Command` types and 
override only `__init__`, `__do__` and `__undo__` in those subclasses

### base class of:

* etllib.commands.AlwaysSucceeds
* etllib.commands.CreateDir
* etllib.commands.CreateTextFile

### properties

`done`
: when `True`, indicates an already executed command.

`failed`
: returns `True` when either the `do` or the `undo` methods
have failed.

`failed_doing`
: when `True`, indicates an exception or an
 ill-terminated subcommand during the invocation of this `Command`
 instance `do` method.

`failed_undoing`
: when `True`, indicates an exception or an
ill-terminated subxommand during the invocation of the `undo` method.

`failure`
: returns the exception that occurred during the last `do` or
`undo` call.


`done_failure`
: returns the specific exception that was raised during 
the execution of the `do` method if any.

`undone_failure`
: returns the specific exception that was raised during 
the execution of the `undo` method if any.


`succeeded`
: returns `True` if no exception was raised during the last
invocation of `do` or `undo`.


`succeeded_doing`
: returns `True` if no exception was raised during
the last execution of the `do` method.

`succeeded_undoing`
: returns `True` if no exception was raised during
the last execution of the `undo` method.


`undone`
: when `True`, indicates an undone command.


### methods

`add_subcommand(self, cls, *args, name=None, **kwargs)`
: appends a subcommand as an instance of class `cls`to the command
on which it is invoked. When no `name`is provided, a generated name
is given to this instance. `args` and `kwargs` are used to instantiate
the subcommand instance as in `cls(*args, **kwargs)`

`do(self, reraise=False)`
:   executes the command. If subcommands were added, they are invoked
after the main command and executed in the order tey were added in
a FIFO manner. 
The `reraise` parameter can be set to `True` to raise to the caller
any exception that occurred during the process of executing the command
and its subcommands.

`undo(self, reraise=False)`
:   reverts the result of the `do` operation. All subcommands are first
undone in the reverse order they were added. Then, the parent command
is itself undone. Set `reraise` to `True` if you want any exception 
that occurred during the undo process of the commands or its 
subcommands to be raised to the caller.

`visit(self, callback, prefix=True)`
: implements the Visitor pattern for a `Command` and its subcommands by
executing recursively the callback for each `Command` instance. 
`callback` must be a callable that accepts only one argument. `callback`
is passed the reference to the command being visited.
Set `prefix` to `False` if you want to visit all subcommands 
before visiting
the parent command.

## class `CreateDir`
`CreateDir(path, *args, **kwargs)`
: creates a new directory. `path` is a relative or
absolute system path to the new directory.


## class `CreateTextFile`
`CreateTextFile(filename, path, *args, content=None, **kwargs)`
: creates a new text file with optional content. `path` must point to a
valid directory. `content` may be any string-like object.


## class `AlwaysSucceeds`
`AlwaysSucceeded(*args, **kwargs)`
:   Dummy `Command` class for testing purposes.





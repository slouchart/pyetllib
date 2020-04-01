# `etllib.utils` — miscellaneous utilities
---

## decorator function `authentication`
`authentication(envvar_prefix='')`
 decorates a callback function to add command line options (thanks to
`click.option` decorators) pertaining to user
authentication by hiding all the internal usage protocol of the class
[`etllib.utils.PasswordReader`](#bookmark1) .

This decorator accepts a `envvar_prefix` parameter that is directly 
transmitted to the constructor of a `PasswordReader` instance.

The options this function adds are as follows:

* `-U <user>`, `--username=<user>`
* `-W/-w`, `--password/--no-password` (defaults to `--password`)

The default value of the flag `password` asks the user to input a 
password from the command prompt.

When the `--no-password` option is set, the function uses a 
`PasswordReader` to get the password by any mean available whether
accessing and checking the `<user>:<password>` pair from environment 
variables or getting it from a password file.

The relevant environment variables are defined within the 
`PasswordReader` instance using the `envvar_prefix` provided as an 
argument.

### example

``` python
@click.command()
@authentication(envvar_prefix='ITSM_')
@click.option('-H', '--url', envvar='ITSM_URL', metavar='<url>',
              help="The URL of iTop server")
def dhcp(ctx, *args, **kwargs):
    pass
```

### retrieving the options value
By default, the username and the password are set within a 
`click.Context` object. To retrieve these values, a bit of boilerplate
code is needed as shown in the snippet below. You can avoid this by 
using the `bare_context_command_callback` decorator.

``` python
# ctx is an instance of click.Context passed to the command callback
# as its first argument.
context = create_exec_context(**ctx.params)

# ctx.obj is an instance of ExecContext set within the authentication
# decorator
context.update(**ctx.obj)
```

## decorator function `bare_context_command_callback`
`bare_context_command_callback(func)`
decorates the callback of a `click.Command` such as its only
parameter in an `ExecContext` initialized with
all option and argument values.

Without the use of this decorator, your callback signature must include
`*args` and `**kwargs` in addition of a first positional parameter
that holds the `click.Context` instance. You must again access this
context `obj` property and its `params` property to access the data.

Of course, you should declare to `Click` you want the `Context` to be 
passed by using the `click.pass_context` and/or `click.pass_obj` 
decorators before using this 
decorator. If you use an `etllib.utlcli` decorator such as `authentication`, the 
`pass_context/obj` stuff is already being taken care of so you don't 
need to repeat yourself.

### example
``` python
@click.command()
@click.pass_context
@bare_context_command_callback
def my_command_callback(context):
    assert isinstance(context, ExecContext)
```

### retrieving the options value
You get the value of each option or argument by accessing the 
`ExecContext` with the option/argument name.

``` python
@click.command()
@click.pass_obj
@click.pass_context
@click.option('-b', is_flag=True, default=False)
@click.argument('arg')
@bare_context_command_callback
def my_command_callback(context):
    opt_b = context.b
    arg = context.arg
```

## decorator function `log_timed_statistics`
`log_timed_statistics(logger_name=None)`
: decorates a function to log the elapsed time of any synchronous 
call to this function.

<a name="bookmark1"></a>
## class `PasswordReader`
`PasswordReader(envvar_prefix='', envvar_user='', envvar_password='', 
envvar_passfile='')`
: utility class that reads and checks passwords from environment
variables or from a password file. The parameters of the `__init__`
method are used internally to define the name of each relevant
 environment variables. You can specify a prefix for each of these
 names by setting `envvar_prefix` to a non-empty value. By default, 
 the name of the environment variables are defined through the class
 variables (see below).

### class variables

`envvar_user`
: sets the name of the environment variable that should contain the 
name of the user. Default to `'USER'`.
 
`envvar_password`
: sets the name of the environment variable that should contain the
password of the user pointed by the variable `envvar_user`. Defaults 
to `'PASSWORD'`.
  
`envvar_passfile`
 : sets the full path of a file that contains users' credentials in the 
 form of <user>:<password> lines. Defaults to `'IDPASSFILE'`.

### properties

`envvars` 
: an instance of `namedtuple` that contains the actual names of
environment variable.

* `envvars.username` : points to the name of the environment variable
that contains the name of the user being checked for password.
* `envvars.password` : points to the name of the environment variable
that contains the password being checked.
* `envvars.passfile` : points to the name of the environment variable
that contains the path of the password file.

### methods

`read_password_from_env(self, expected_user)`
: reads the value of the environment variable pointed by 
`self.envvars.username` and if it is equal to `expected_user`, returns
the value pointed by the variable name in `self.envvars.password`
considered the credentials to be checked positively. Raises a 
`ValueError` if there is a mismatch between the username provided as an
argument and the username read from the environment.

`read_password_from_file(self, username)`
: scans the contents of the file pointed by the value of 
`self.envvars.passfile` for a line containing `<username>:<password>`
and returns the value at `<password>`. Raises a `RuntimeError` if no
match can be found in the file or if the file cannot be read.

> *Note: for now, this method does not perform any check on the file
> permissions. Anyway, most password files should have special
> permissions such as 400 to ensure a correct level of security.*

Both methods raise a `RuntimeError` if any environment variable cannot
be read. 

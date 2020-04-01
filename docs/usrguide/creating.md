# Creating a project structure for an ETL script

--- 

## Basic invocation of `etlskel`
The default behaviour of `etlskel` creates a project structure 
containing the following items:
``` vim
$ etlskel my_etl_script
...
my_etl_script
|
│   MANIFEST.in
│   README.md
│   setup.py
│
├───my_etl_script
│   │   cli.py
│   │   extract.py
│   │   publish.py
│   │   transform.py
│   │   __init__.py
│   │
│   └───templates
│           __init__.py
│
└───tests
        __init__.py

```

## Features
Although the naming of the directories is pretty straightforward, you 
may need some guidelines on where to put which files of your project 
and on how to structure your code in the Python modules.

### the `templates` directory
If you intent to publish your data to some text files, it is easier 
to format using Jinja templates (see Jinja project documentation 
[here](https://jinja.palletsprojects.com/en/2.10.x/)). To do so, 
simply stash your template files with the extension `*.j2` into 
this directory. 

This has two benefits. First, the `load_template` function will manage 
to cate your template file without any hassle and, second, your 
template file will automatically be part of your distribution thanks 
to the `MANIFEST` file.
If you happen to not need any template, simply invoke `etlskel` 
with the `--no-template-dir` option.

### the `tests` directory
A good project shall always include some unit and integration testing. 
`etlskel` includes a directory apart from your project root package 
directory in order to store your test modules. 

If you do not want this directory to be created, simply tells 
`etlskel` not to do so by specifying the `--no-test-package` 
options on the command line.

### Main package name

By default, the project root directory and the main package inside 
it share the same name. You can override this behaviour by specifying 
the option `--package-name <my_package>` when you invoke `etlskel`.
For instance, invoking
``` vim
$ etlskel --package-name foo my_etl
```
results in the following directory structure:
```vim
my_etl
├───foo
│   └───templates
└───tests
```


### `setuptools` configuration
The project structure creation process always includes a `setup.py` 
file under the project directory. This file contents are for a large 
part guessed from the few options `etlskel`accepts but it is up to you 
to fill in the blanks. We suppose you know the drill, if not, please 
read [some fundamentals](https://packaging.python.org/tutorials/packaging-projects/) 
on this subject.

A setup parameter of special consideration is the `entry_points` 
argument of the `setup` function.
``` vim
[recetl_plugins]
<entry_point>=<package>:<function>
```

If your main package name is, let's say, `foo`, the entry point of 
your script will be:
```vim
foo=foo.cli:foo
```

It means that the `foo.cli` module **MUST** _contain_ and _export_ a 
function named `foo()`.
Additionally, this function **MUST** be decorated using a `Click` 
decorator (`command`, `group` and so on) so the exported entry point 
is a subtype of `Click.Command` as the plugin loader of `recetl run` 
expects.

## Creating a source directory
It is considered a best practice to put all your source files under a 
specific directory. Whether or not doing so is *really* a best practice 
is still debated. You can read more about 
[packaging a python library here](https://blog.ionelmc.ro/2014/05/25/python-packaging/).
By default, `etlskel` deploys your source under the main project 
directory at the same level with the `tests` module. The `setup` 
configuration takes care to find the right package to consider when it 
comes to build or install your package.
If you happen to need a `src` directory, just tell `etlskel` with 
the `--source-dir` option.
``` vim
$ etlskel --source-dir --package-name foo my_etl

my_etl
├───src
│   └───foo
│       └───templates
└───tests
``` 
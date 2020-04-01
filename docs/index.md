# `pyetllib` ETL Framework

Implementing and deploying ETL scripts in Python

--- 

## Overview

The `pyetllib` ETL Framework is a toolkit that eases writing your own ETL 
(Extract-Transform-Load) utilities with Python. Start by reading the 
introduction below, then jump to the [User Guide](usrguide/getstarted.md)
 for more info about how 
to start implementing your own ETL script.

## Scripts as Plugins

A ETL script is a Python program that contains a specifically 
named entry point in its `setup.py` file. This allows the script 
to be dynamically loaded as a subcommand of the main launcher 
command `pyetl run`. So, in order to execute your script, 
provided that you have it installed, simply run the launcher.

``` bash
$ pyetl run myscript
```

`pyetl` can even list the locally available plugins.

``` bash
$ pyetl show plugins
dhcp    dns    stats
```

In addition each script may have any command-line options and/or 
arguments. We recommend you to use the Python third-party 
package `Click` ([read their doc!](https://click.palletsprojects.com/en/7.x/))
as it is a wonderful toolkit to create slick 
Command Line Interfaces. `pyetllib` ETL Framework CLI is even built 
with `Click`.

## Common project structure

Each ETL script project should share a common structure that is 
highlighted below.

``` vim
│   MANIFEST.in
│   README.md
│   setup.py
│
├───<project_dir>
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

In order to achieve that, `pyetllib` ETL Framework provides you 
`etlskel`, a utility program that creates the project structure for you. 
To learn more on how `etlskel` works, 
please read [Creating an ETL script](usrguide/creating.md)

# ETL tools and utilities

The `etllib` package exports some tools to ease the process 
of creating ETL data pipelines. Please read the relevant 
section in the [User Guide](usrguide/etltk.md)



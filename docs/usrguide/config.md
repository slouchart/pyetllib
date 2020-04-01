# The `pyetl` configuration file

--- 

## File location
If your script implements a file based configuration using 
`pyetl.etllib.config`, there exists several possible locations for
the configuration file `pyetl.config.toml`:

* the current directory
* the user home directory
* `/etc/pyetl` (**on Linux**)
* `%LOCALAPPDATA%\pyetl` and `%APPDATA%\pyetl` (**on Windows**)

Alternatively, you can provide your configuration file as part as 
the distribution of your plugin. We recommend to create a package 
`config` under your plugin main package and to put the configuration
file at this location:

```
etl-foo
|
│   MANIFEST.in
│   README.md
│   setup.py
│
└───foo
    │   cli.py
    │   extract.py
    │   publish.py
    │   transform.py
    │   __init__.py
    |
    └───config
            pyetl.config.toml
            __init__.py
```

## Content
The `pyetl.config.toml` is a text-based, UTF-8 encoded file using the
TOML specification format. TOML stands for "Tom's Obvious, Minimal 
Language". You can learn more about this format in its 
[Wikipedia entry](https://en.wikipedia.org/wiki/TOML) and you can read
the TOML language specification 
on [GitHub](https://github.com/toml-lang/toml#toml).

The following basic structure is mandatory for the configuration file
to be successfully parsed by the API:
```
[pyetl]
# Common section 

[plugins]
# Plugins section

```

The plugin-specific configuration must belong to its own section 
under the `[plugins]` section. Example given for a plugin named `foo`:
```
[pyetl]
# Common section 

[plugins]
# Plugins section

[plugins.foo]
description = "A really cool plugin"

```

## API
The `PluginConfig` API and the underlying `ConfigLoader` classes are 
described in the [API Reference](../apiref/config.md).
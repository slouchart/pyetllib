# `etllib.config` — configuration utilities

--- 

## class `PluginConfig`

`PluginConfig(app_name, plugin_name, loader_factory)` instantiates a 
proxy object able to read a plugin configuration from various sources:

* a regular file-system file in the TOML format
* a TOML file in a package
* a string-like object containing the TOML code

The initialization parameters directly map the properties of the 
instance that are described in the next section.

### properties

`app_name`
the name of the application whose configuration is to be 
loaded. Used by `ConfigFileLoader` and `ConfigPackageLoader`
to identify the configuration file.

`plugin_name` the name of the application plugin whose configuration
is to be loaded. Used internally to retrieve the relevant section of 
the configuration.

`loader_factory` a callable that returns an instance of `ConfigLoader`

### methods

`load(*args, **kwargs)` returns the configuration as a `dict`. Its 
arguments are directly passed to `loader_factory` as part of 
the process.

## Loaders
Three concrete loader classes are currently implemented.

`ConfigFileLoader(app_name, *args, **kwargs)` creates a loader to 
retrieve the configuration from any regular file. The name of that file
is formatted as `'{app_name}.config.toml'`

`ConfigPackageLoader(app_name, package_name)` creates a loader to 
retrieve the configuration from a package file. The `package_name` must
be an absolute package reference as a string like, for instance, 
`'foo.bar'`.

`ConfigTextLoader(app_name, text)` creates a loader to load the 
configuration from a string-like object passed as `text`.
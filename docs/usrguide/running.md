# Running an ETL script as a plugin

---

Congratulations! You now have a new ETL script implemented from the 
skeleton project created with `etlskel`. Packaging and deployment 
follow the common rules of any Python library and you should not 
have any issue with that.

## Installing an ETL script as a plugin
Follow the rules you have defined to deploy your package. Usually 
you may want to use `pip` because it's easy. Once this done, you can 
check if your ETL package appears as a registered plugin with `pyetl`. 
Simply enter `pyetl show plugins` and your plugin's entry points 
should appear in the output list.

```vim
$ pyetl show plugins
dhcp dns foo <-- your plugin!
``` 

## Calling for help
You can also check whether your plugin correctly displays its usage 
text:
```
$ pyetl run foo --help
```

## Running your ETL script
Your plugin is registered as a subcommand of `pyetl` `run`command. 
To execute it, simply invoke the launcher:
``` bash
$ pyetl run foo [<my_plugin_optios>] [my_plugin_args]
```

## Uninstalling your ETL script
Because your plugin is basically a site-installed Python package which 
is dynamically loaded by the launcher on execution, you don't need to 
be specially careful about uninstalling. Here again, use `pip` with 
the `uninstall` command.


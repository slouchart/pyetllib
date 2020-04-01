# `etlskel` — Command Line Interface

``` vim
Usage: etlskel [OPTIONS] <project name>

Options:
  --template-dir / --no-template-dir 
                                     
  -p, --package-name <name>          
                                     
  -s, --source-dir                   
  
  -T, --no-test-package 
  
  -b, --bare
```

## argument `<project name>`
Specifies the name of your ETL script. This name is used to create 
the project main directory and as a default name for the main package.

## option `--template-dir / --no-template-dir`
Creates a package for Jinja2 template files under the main package
directory. 

Defaults to `--template-dir`. Use explicitly the
`--no-template-dir` option if your project does not need Jinja 
rendering.

## option `--package-name <name>`
Specifies a different name for the main package. By default, the main 
package and the main project directory share the same name.

## option `--source-dir`
Collates all Python sources under a `src` directory under the project
main directory. The default behaviour creates both the main package
directory and the `tests` directory under the project root directory.

## option `--no-test-package`      
Skips the creation of the unit testing package.

## option `--bare`
*New in version 0.4.2*

Creates a bare project without tox/git init files.

The default is to create both `tox.ini` and `.gitignore` at the
project root.


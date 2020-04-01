# Using the Tox interface

---

## Available Tox environments
The `tox` layout is pretty standard and can be found running `tox -av` 
on the command line:
```
$ tox -av
default environments:
test       -> Unit testing with Python 3.6 and unittest
style      -> Style Guide Enforcement

additional environments:
cover      -> Code coverage
build      -> Build wheel distribution of the package
docs-build -> Build HTML documentation
docs-devel -> Develop MarkDown documentation
```

## Testing 
The following conventions apply to unit testing files:

* a unit file name **MUST** start with `test`
* a unit file **MUST** be located in the `tests` directory

Following these conventions ensures the file will be considered 
by `tox`. To start a manual unit testing session, simply run the 
command `tox -e test`

## Style enforcement
As part of unit testing is style enforcement which is also started 
by Tox and performed by the `flake8` package. **All style constraints**
defined by [PEP 8](https://pep8.org/) are enforced.

Check the code for style errors and warnings by running `tox -e style`.
Please note that invoking `tox` without any options runs *both* the unit
tests and the code style checks!

## Code coverage
Code coverage operated by unit testing can be measured and reported
with a dedicated tox environment. Use `tox -e cover` to run the code
coverage process. This command displays the coverage report 
on the standard output

## Building
The `tox -e build` command automatically start building the `pyetllib`
 ETL Framework into a `wheel` universal distribution. The `*.whl` file 
 can then be accessed from within the `dist` directory. Deploying the 
resulting distribution to an artifact repository is still
out of scope.

## Building the documentation
As part of the distribution is building the HTML static pages from the 
Markdown sources. To perform this, simply run `tox -e docs-build` and
gather the produced files from the `site` directory. You can manually
deploy these pages to an HTTP server. Automatic deployment to a 
documentation server such as [Read the Docs](https://readthedocs.org/)
 is still out of scope.


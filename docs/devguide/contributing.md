# Contributing to `pyetllib` ETL Framework

---

## Get the sources
Use `git clone` to clone the remote GitLab repository available 
(for now) at this URL:

```
https://gitlab.escolan.recia.fr/sebastien.louchart/recia-etl.git
```

Follow by a `git fetch` to refresh all the branches from the origin and
then complete the procedure by switching to the branch `develop` with
`git checkout develop`


## Setup a virtual environment
We recommend the use of PyCharm as an IDE for Python.
Once you have cloned the remote git repository, open the project in 
PyCharm and set up a new virtual environment (File->Settings->Project
->Project Interpreter) based on Python 3.6. 

Then, configure the project requirements by running `pip install -e .`

## Start working on a feature
Create a new branch from the branch `develop` and don't forget to 
`git add` any new file and to `git commit` on a regular basis.

## Working with GitLab
Once you're done with your feature (implemented, tested and covered), 
you can push your changes on GitLab using `git push`. Your branch will 
be reviewed and merged into the main `develop` branch.


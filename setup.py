from setuptools import setup, find_packages
import io


with io.open('README.md') as f:
    readme = f.read()

setup(
    name="pyetllib",
    version="0.0.0",
    description='Common tools for ETL scripting',
    long_description=readme,
    package_dir={"": "src"},
    packages=find_packages(where='src', exclude=('tests',)),
    author='Sébastien LOUCHART',
    author_email='sebastien.louchart@gmail.com',
    license='MIT',
    install_requires=[
        'Click',
        'Jinja2',
        'toolz',
        'toml'
    ],
    entry_points='''
        [console_scripts]
        etlskel=pyetllib.etlskel.cli:etlskel
        pyetl=pyetllib.launcher.cli:pyetl
        ''',
    include_package_data=True,
    package_data={
        'etlskel.templates': ['*.j2'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Systems Administration',
    ]
)

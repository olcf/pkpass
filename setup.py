#!/usr/bin/env python
# Note: to use the 'upload' functionality of this file, you must:
# $ pip install twine

from __future__ import print_function
import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data
NAME = 'pkpass'
DESCRIPTION = 'Public Key based password manager'
URL = 'https://github.com/olcf/pkpass'
EMAIL = 'ginsburgnm@gmail.com'
AUTHOR = 'Noah Ginsburg'
VERSION = None

REQUIRED = [
    'asn1crypto==0.24.0',
    'cffi==1.11.4',
    'cryptography==2.1.4',
    'enum34==1.1.6',
    'future==0.17.1',
    'idna==2.6',
    'ipaddress==1.0.19',
    'nginsecretsharing==0.3.0',
    'pbr==5.1.1',
    'pycparser==2.18',
    'pyperclip==1.6.0',
    'PyYAML==3.12',
    'six==1.11.0',
    'utilitybelt==0.2.6'
]

EXTRAS = {
    'testing': ['mock']
}

HERE = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
        LONG_DESCRIPTION = '\n' + f.read()
except IOError:
    LONG_DESCRIPTION = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
ABOUT = {}
if not VERSION:
    PROJECT_SLUG = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(HERE, PROJECT_SLUG, 'VERSION')) as version_file:
        ABOUT['__version__'] = version_file.read().strip()
else:
    ABOUT['__version__'] = VERSION

def user_input(prompt, default):
    u_input = raw_input(prompt).strip()
    return u_input if u_input else default

def directory_creation(user_prompt, default):
    directory = user_input(user_prompt, default)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    return str(directory)

def file_creation(user_prompt, default):
    fname = user_input(user_prompt, default)
    if not os.path.exists(fname):
        with open(fname, 'a'):
            os.utime(fname, None)
    return str(fname)

PASSDB_HOME = os.path.join(str(os.path.expanduser("~")), "passdb")
CERTS = directory_creation("Directory for certpath (defaults to ~/passdb/certs): ",
                           os.path.join(PASSDB_HOME, "certs"))
KEYS = directory_creation("Directory for keypath (defaults to ~/passdb/keys): ",
                          os.path.join(PASSDB_HOME, "keys"))
CABUNDLE = file_creation("Path to cabundle (defaults to ~/passdb/cabundles/ca.bundle): ",
                         os.path.join(PASSDB_HOME, "cabundles", "ca.bundle"))
PASSWORDS = directory_creation("Directory for passwords (defaults to ~/passdb/passwords): ",
                               os.path.join(PASSDB_HOME, "passwords"))


class UploadCommand(Command):
    """Support setup.py upload."""
    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(string):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(string))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds..')
            rmtree(os.path.join(HERE, 'dist'))
        except OSError:
            pass

        self.status('Building source and wheel distribution..')
        os.system('{0} setup.py sdist bdist_while --universal'.format(sys.executable))

        self.status('Uploading the package to pypi via twine..')
        os.system('twine upload dist/*')

        self.status('Pushing git tags..')
        os.system('git tag v{0}'.format(ABOUT['__version__']))
        os.system('git push --tags')

        sys.exit()

setup(
    name=NAME,
    version=ABOUT['__version__'],
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='GPLV3',
    classifiers=[
        'License :: OSI Approved :: GNU GENERAL PUBLIC LICENSE V3 (GPLV3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        ],
    cmdclass={
        'upload': UploadCommand,
        },
    )

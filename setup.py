#!/usr/bin/env python
# Note: to use the 'upload' functionality of this file, you must:
# $ pip install twine

from __future__ import print_function
import yaml
import io
import os
import sys
from subprocess import Popen, PIPE, STDOUT
import getpass
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
    with open(os.path.join(HERE, 'VERSION')) as version_file:
        ABOUT['__version__'] = version_file.read().strip()
else:
    ABOUT['__version__'] = VERSION

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

class RCFile(Command):
    """Re/Create RCFile"""
    description = 'Create a pkpass rc file'
    user_options = []

    def initialize_options(self):
        self.home = os.path.expanduser("~")

    def finalize_options(self):
        # this command object complains with you do stuff in init
        self.home = os.path.expanduser("~") #pylint: attribute-defined-outside-init

    def user_input(self, prompt, default):
        u_input = raw_input(prompt).strip()
        return u_input if u_input else default

    def directory_creation(self, user_prompt, default):
        directory = self.user_input(user_prompt, default) if user_prompt else default
        directory = os.path.expanduser(directory)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        return str(directory)

    def file_creation(self, user_prompt, default):
        filename = self.user_input(user_prompt, default)
        filename = os.path.expanduser(filename)
        if not os.path.exists(filename):
            self.directory_creation(None, os.path.dirname(filename))
            with open(filename, 'w+') as newfile:
                newfile.write("")
        return str(filename)

    def finish_run(self):
        testing = """testing versions of openssl and pkcs15-tool if version numbers return you're probably good
        for sanity sake Noah's return values were: 
        openssl version: LibreSSL 2.2.7
        pkcs15-tool --version: OpenSC-0.18.0, rev: eb60481f, commit-time: 2018-05-16 13:48:37 +0200
        ------YOUR VALUES BELOW THIS LINE -----------"""

        print(testing)
        print(Popen("openssl version".split(), stdout=PIPE, stdin=PIPE, stderr=STDOUT).communicate()[0])
        print(Popen("pkcs15-tool --version".split(), stdout=PIPE, stdin=PIPE, stderr=STDOUT).communicate()[0])

    def run(self):
        print("If not using defaults for the following paths please use full filepath or relative to home using ~")
        passdb_home = os.path.join(self.home, "passdb")
        certs = self.directory_creation("Directory for certpath (defaults to ~/passdb/certs): ",
                                        os.path.join(passdb_home, "certs"))
        keys = self.directory_creation("Directory for keypath (defaults to ~/passdb/keys): ",
                                       os.path.join(passdb_home, "keys"))
        cabundle = self.file_creation("Path to cabundle (defaults to ~/passdb/cabundles/ca.bundle): ",
                                      os.path.join(passdb_home, "cabundles", "ca.bundle"))
        passwords = self.directory_creation("Directory for passwords (defaults to ~/passdb/passwords): ",
                                            os.path.join(passdb_home, "passwords"))

        print(Popen("pkcs11-tool -L".split(), stdout=PIPE, stdin=PIPE, stderr=STDOUT).communicate()[0])
        card_slot = self.user_input("Available slots listed above, which would you like to use? (defaults to 0): ", "0")
        identity = self.user_input("What user name would you like to use? (defaults to system user): ", getpass.getuser())
        print("Escrow users is a feature of Pkpass. Escrow allows a password to be recovered by the majority of the escrow users in the event of an emergency.")
        check_escrow = self.user_input("Would you like to setup escrow? ", "n")
        if check_escrow.lower()[0] != 'y':
            escrow_users = ""
            min_escrow = ""
        else:
            escrow_users = self.user_input("Please enter a comma seperated list of usernames: ", "").split(',')
            escrow_users = ",".join([user.strip() for user in escrow_users])
            min_escrow = self.user_input("What should be the minimum number of escrow users required to unlock? ",
                                         len(escrow_users.split(',')) - 1)

        contents = """certpath: %s
keypath: %s
cabundle: %s
pwstore: %s
card_slot: %s
identity: %s
escrow_users: %s
min_escrow: %s""" % (certs, keys, cabundle, passwords, card_slot, identity, escrow_users, min_escrow)

        with open(os.path.join(self.home, '.pkpassrc'), 'w') as fname:
            fname.write(contents)

        self.finish_run()

class verify(Command):
    """Verify the RC file is still valid
    use this with:
        python setup.py verify -r "/path/to/.pkpassrc" """
    description = 'Lints the pkpassrc file'
    user_options = [("rcfile=", "r", 'Specify the rc file path')]

    def initialize_options(self):
        self.rcfile = ""

    def finalize_options(self):
        pass

    def check_if_recipient(self, user, certpath):
        for fname in os.listdir(certpath):
            if fname.endswith(tuple(['.crt','.cert'])):
                uid = fname.split('.')[0]
                if uid == user:
                    return True
        return False

    def check_users(self, args_dict, certpath, valid):
        args = ['escrow_users', 'groups', 'identity','users']
        for arg in args:
            users_list = []
            if arg in args_dict.keys():
                if args_dict[arg]:
                    users_list = args_dict[arg].strip().split(',')
                    for user in users_list:
                        if not self.check_if_recipient(user.strip(), certpath):
                            valid = False
                            print("'%s' found in config, not in recipientsdb" % user)
                else:
                    valid = False
                    print("'%s' found in config, but value is empty" % arg)
        return valid

    def check_paths(self, args_dict, valid):
        args = ['cabundle', 'certpath', 'dstpwstore','pwstore']
        for arg in args:
            if arg in args_dict.keys():
                if not os.path.exists(args_dict[arg]):
                    valid = False
                    print("'%s' found in config, No such file or directory: %s" % 
                            (arg, args_dict[arg]))
        return valid

    def run(self):
        valid = True
        args = ['cabundle', 'card_slot', 'certpath',
                'connect', 'dstpwstore', 'escrow_users',
                'groups', 'identity', 'keypath',
                'min_escrow', 'pwstore', 'time',
                'rules', 'rules_map', 'users']
        store_args = ['all', 'ignore_decrypt', 'long_escrow',
                      'noescrow', 'nocrypto', 'nopassphrase',
                      'nosign', 'noverify','overwrite',
                      'pwfile', 'pwname', 'recovery', 'stdin']
        args_dict = {}
        with open(self.rcfile, 'r') as rcyaml:
            try:
                args_dict = yaml.safe_load(rcyaml)
            except yaml.YAMLError as err:
                valid = False
                print(err)
        for arg in store_args:
            if arg in args_dict.keys():
                valid = False
                print("'%s' found in rc file, this will be ignored" % arg)

        for arg in args_dict.keys():
            if arg not in args and arg not in store_args:
                valid = False
                print("'%s' found in rc file, does not appear to be valid argument\
(It may be a user defined group)" % arg)

        if 'certpath' in args_dict.keys():
            valid = self.check_users(args_dict, args_dict['certpath'], valid)

        valid = self.check_paths(args_dict, valid)
        if valid:
            print("Config Valid")

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
        'rcfile': RCFile,
        'verify': verify,
        },
    scripts=[
        'bin/pkpass'
        ]
    )

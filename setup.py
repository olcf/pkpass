#!/usr/bin/env python3
# Note: to use the 'upload' functionality of this file, you must:
# $ pip install twine
import os
import shutil
from shutil import rmtree
import sys
from subprocess import Popen, PIPE, STDOUT
import getpass
from setuptools import setup, Command
import versioneer

REQUIRED = [
    'colored==1.4.2',
    'cryptography==3.4.7',
    'exrex==0.10.5',
    'mock==4.0.3',
    'pem==21.2.0',
    'pyperclip==1.8.2',
    'pyseltongue==1.0.0',
    'python-dateutil==2.8.1',
    'PyYAML==5.4.1',
    'setuptools==56.0.0',
    'SQLAlchemy==1.4.27',
    'tqdm==4.60.0',
    'ruamel.yaml==0.17.4',
    'ruamel.yaml.clib==0.2.2',
]

HOME = os.path.expanduser("~")
HERE = os.path.abspath(os.path.dirname(__file__))

def rcfile_check():
    rc_location = os.path.join(HOME, ".pkpassrc.yaml")
    example_location = os.path.join(HERE, 'example_pkpassrc')
    if os.path.exists(rc_location):
        if os.path.isdir(rc_location):
            print("WARN: default rc file location is a directory")
        else:
            print(".pkpassrc already defined, skipping")
            return
    else:
        print("Copying example rc file to %s" % rc_location)
        shutil.copyfile(example_location, rc_location)

# Load the package's __version__.py module as a dictionary.
ABOUT = {}

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
        pass

    def finalize_options(self):
        pass

    def user_input(self, prompt, default):
        u_input = input(prompt).strip()
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
        print(Popen("openssl version".split(), stdout=PIPE, stdin=PIPE, stderr=STDOUT).communicate()[0].decode("ASCII"))
        print(Popen("pkcs15-tool --version".split(), stdout=PIPE, stdin=PIPE, stderr=STDOUT).communicate()[0].decode("ASCII"))

    def run(self):
        args = {
            'cabundle': '',
            'card_slot': '',
            'certpath': '',
            'connect': '',
            'escrow_users': '',
            'groups': '',
            'identity': '',
            'keypath': '',
            'min_escrow': '',
            'pwstore': '',
            'time': '',
            'rules': '',
            'rules_map': '',
            'users': ''
            }
        print("If not using defaults for the following paths please use full filepath or relative to home using ~")
        passdb_home = os.path.join(HOME, "passdb")
        args['certpath'] = self.directory_creation("Directory for certpath (defaults to ~/passdb/certs): ",
                                                   os.path.join(passdb_home, "certs"))
        args['keypath'] = self.directory_creation("Directory for keypath (defaults to ~/passdb/keys): ",
                                                  os.path.join(passdb_home, "keys"))
        args['cabundle'] = self.file_creation("Path to cabundle (defaults to ~/passdb/cabundles/ca.bundle): ",
                                              os.path.join(passdb_home, "cabundles", "ca.bundle"))
        args['pwstore'] = self.directory_creation("Directory for passwords (defaults to ~/passdb/passwords): ",
                                                  os.path.join(passdb_home, "passwords"))

        print(Popen("pkcs11-tool -L".split(), stdout=PIPE, stdin=PIPE, stderr=STDOUT).communicate()[0].decode("ASCII"))
        args['card_slot'] = self.user_input("Available slots listed above, which would you like to use? (defaults to 0): ", "0")
        args['identity'] = self.user_input("What user name would you like to use? (defaults to system user): ", getpass.getuser())
        print("Escrow users is a feature of Pkpass. Escrow allows a password to be recovered by the majority of the escrow users in the event of an emergency.")
        check_escrow = self.user_input("Would you like to setup escrow? ", "n")
        if check_escrow.lower()[0] == 'y':
            escrow_users = self.user_input("Please enter a comma seperated list of usernames: ", "").split(',')
            args['escrow_users'] = ",".join([user.strip() for user in escrow_users])
            args['min_escrow'] = self.user_input("What should be the minimum number of escrow users required to unlock? ",
                                                 len(args['escrow_users'].split(',')) - 1)

        with open(os.path.join(HOME, '.pkpassrc'), 'w') as fname:
            # fname.write(contents)
            for key, value in args.items():
                if value:
                    fname.write("%s: %s\n" % (key, value))
                else:
                    fname.write("#%s:\n" % key)

        self.finish_run()

class Verify(Command):
    """Verify the RC file is still valid
    use this with:
        python setup.py verify -r "/path/to/.pkpassrc" """
    description = 'Lints the pkpassrc file'
    user_options = [("rcfile=", "r", 'Specify the rc file path')]

    def initialize_options(self):
        self.rcfile = "~/.pkpassrc"

    def finalize_options(self):
        pass

    def check_if_recipient(self, user, certpath):
        for fname in os.listdir(certpath):
            if fname.endswith(tuple(['.crt', '.cert'])):
                uid = fname.split('.')[0]
                if uid == user:
                    return True
        return False

    def check_users(self, args_dict, certpath, valid):
        args = ['escrow_users', 'groups', 'identity', 'users']
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
        args = ['cabundle', 'certpath', 'pwstore']
        for arg in args:
            if arg in args_dict.keys():
                if not os.path.exists(args_dict[arg]):
                    valid = False
                    print("'%s' found in config, No such file or directory: %s" %
                          (arg, args_dict[arg]))
        return valid

    def run(self):
        import yaml
        valid = True
        args = ['cabundle', 'card_slot', 'certpath',
                'connect', 'escrow_users',
                'groups', 'identity', 'keypath',
                'min_escrow', 'pwstore', 'time',
                'rules', 'rules_map', 'users',
                'theme_map', 'color']
        store_args = ['all', 'ignore_decrypt', 'long_escrow',
                      'noescrow', 'nocrypto', 'nopassphrase',
                      'nosign', 'noverify', 'overwrite',
                      'pwfile', 'pwname', 'recovery', 'stdin']
        args_dict = {}
        if self.rcfile:
            with open(os.path.expanduser(self.rcfile), 'r') as rcyaml:
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

CMDCLASS = versioneer.get_cmdclass()
CMDCLASS['upload'] = UploadCommand
CMDCLASS['rcfile'] = RCFile
CMDCLASS['verify'] = Verify
setup(
    version=versioneer.get_version(),
    install_requires=REQUIRED,
    extras_require={
        'testing': ["mock", "tox"]
    },
    cmdclass=CMDCLASS,
    )

try:
    rcfile_check()
except FileNotFoundError as err:
    print("WARN: could not copy example rc file")

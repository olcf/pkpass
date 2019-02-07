"""This module is a generic for all pkpass commands"""

from __future__ import print_function
import getpass
import os
import yaml
from six import iteritems as iteritems
from libpkpass.commands.arguments import ARGUMENTS as arguments
from libpkpass.password import PasswordEntry
from libpkpass.identities import IdentityDB
from libpkpass.errors import NullRecipientError, CliArgumentError, FileOpenError


class Command(object):
    ##########################################################################
    """ Base class for all commands.  Auotmatically registers with cli subparser
    and provides run execution for itself.                                     """
    ##########################################################################

    name = None
    description = None
    selected_args = None
    passphrase = None

    def __init__(self, cli):
        ##################################################################
        """ Intialization function for class. Register with argparse   """
        ##################################################################
        self.cli = cli
        self.args = {'identity': getpass.getuser(),
                     'pwstore': './passwords',
                     'certpath': './certs',
                     'keypath': './private',
                     'cabundle': './certs/ca-bundle',
                     'time': 10,
                     'card_slot': None,
                     'min_escrow': None,
                     'escrow_users': None}
        self.recipient_list = []
        self.identities = IdentityDB()
        cli.register(self, self.name, self.description)

    def register(self, parser):
        ####################################################################
        """ Registration function for class. Register with argparse      """
        ####################################################################
        for arg in sorted(self.selected_args):
            parser.add_argument(
                *arguments[arg]['args'],
                **arguments[arg]['kwargs'])

    def run(self, parsedargs):
        ##################################################################
        """ Passes the argparse Namespace object of parsed arguments   """
        ##################################################################
        self._run_command_setup(parsedargs)
        self._run_command_execution()

    def _run_command_setup(self, parsedargs):
        ##################################################################
        """ Passes the argparse Namespace object of parsed arguments   """
        ##################################################################

        # Build a dict out of the argparse args Namespace object and a dict from any
        # configuration files and merge the two with cli taking priority
        cli_args = vars(parsedargs)

        config_args = self._get_config_args(cli_args['config'])
        self.args.update(config_args)

        fles = ['certpath', 'keypath', 'cabundle', 'pwstore']
        for key, value in iteritems(cli_args):
            if value is not None or key not in self.args:
                self.args[key] = value
            if key in fles and not os.path.exists(self.args[key]):
                raise FileOpenError(self.args[key], "No such file or directory")

        #print self.args
        if self.args['escrow_users']:
            self.args['escrow_users'] = self.args['escrow_users'].split(",")
        self._validate_args()

        if 'nopassphrase' in self.selected_args and not self.args['nopassphrase']:
            self.passphrase = getpass.getpass("Enter Pin/Passphrase: ")

        # Build the list of recipients that this command will act on
        self._build_recipient_list()

        # If there are defined repositories of keys and certificates, load them
        self.identities.load_certs_from_directory(
            self.args['certpath'], self.args['cabundle'])
        self.identities.load_keys_from_directory(self.args['keypath'])
        self._validate_identities()

    def create_pass(self, password1, description, authorizer):
        ####################################################################
        """ Run function for class.                                      """
        ####################################################################
        password_metadata = {}
        password_metadata['description'] = description
        password_metadata['authorizer'] = authorizer
        password_metadata['creator'] = self.args['identity']
        password_metadata['name'] = self.args['pwname']
        if self.args['min_escrow']:
            password_metadata['min_escrow'] = self.args['min_escrow']

        password = PasswordEntry(**password_metadata)

        password.add_recipients(secret=password1,
                                distributor=self.args['identity'],
                                recipients=[self.args['identity']],
                                identitydb=self.identities,
                                passphrase=self.passphrase,
                                card_slot=self.args['card_slot'],
                                escrow_users=self.args['escrow_users'],
                                minimum=self.args['min_escrow']
                               )

        password.write_password_data(os.path.join(
            self.args['pwstore'], self.args['pwname']), overwrite=self.args['overwrite'])

    def _run_command_execution(self):
        ##################################################################
        """ Passes the argparse Namespace object of parsed arguments   """
        ##################################################################
        raise NotImplementedError

    def _build_recipient_list(self):
        try:
            self.recipient_list = self.args['users'].split(',')
            for user in self.recipient_list:
                if str(user) == '':
                    raise NullRecipientError
        except KeyError:  # If this is a command with no users, don't worry about it
            pass

    def _get_config_args(self, config):
        try:
            with open(config, 'r') as fname:
                config_args = yaml.safe_load(fname)
            if config_args is None:
                config_args = {}
            return config_args
        except IOError:
            print("No .pkpassrc file found, consider running ./setup.sh")
            return {}

    def _validate_args(self):
        raise NotImplementedError

    def _validate_identities(self):
        for recipient in self.recipient_list:
            if recipient not in self.identities.iddb.keys():
                raise CliArgumentError(
                    "Error: Recipient '%s' is not in the recipient database" %
                    recipient)

        if self.args['identity'] not in self.identities.iddb.keys():
            raise CliArgumentError(
                "Error: Your user '%s' is not in the recipient database" %
                self.args['identity'])

    def _print_debug(self):
        print(self.recipient_list)
        print(self.identities.iddb.keys())

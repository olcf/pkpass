import argparse
import yaml
import getpass
from arguments import arguments
from libpkpass.identities import IdentityDB
from libpkpass.errors import *


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
                     'ca_bundle_path': './certs/ca-bundle',
                     'time': 10}
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

        for key, value in cli_args.iteritems():
            if value is not None or key not in self.args:
                self.args[key] = value

        #print self.args

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
            with open(config, 'r') as f:
                config_args = yaml.safe_load(f)
            if config_args is None:
                config_args = {}
            return config_args
        except IOError as e:
            raise NoRCFileError

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
        print self.recipient_list
        print self.identities.iddb.keys()

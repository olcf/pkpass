"""This module is a generic for all pkpass commands"""
import getpass
from os import getcwd, path, sep, remove, rename
from libpkpass.commands.arguments import ARGUMENTS as arguments
from libpkpass.crypto import print_card_info
from libpkpass.errors import NullRecipientError, CliArgumentError, GroupDefinitionError,\
        PasswordIOError, NotThePasswordOwnerError
from libpkpass.identities import IdentityDB
from libpkpass.passworddb import PasswordDB
from libpkpass.password import PasswordEntry
from libpkpass.util import collect_args, color_prepare

    ##########################################################################
class Command():
    """ Base class for all commands.  Auotmatically registers with cli subparser
    and provides run execution for itself.                                     """
    ##########################################################################
    name = None
    description = None
    selected_args = ['nocache', 'verbosity', 'quiet', 'identity', 'cabundle',
                     'certpath', 'color', 'theme_map']
    passphrase = None

        ##################################################################
    def __init__(self, cli, iddb=None, pwdb=None):
        """ Intialization function for class. Register with argparse   """
        ##################################################################
        self.cli = cli
        #default certpath to none because connect string is allowed
        self.args = {}
        self.recipient_list = []
        self.escrow_and_recipient_list = []
        self.iddbcached = iddb is not None
        self.identities = iddb if iddb else IdentityDB()
        self.pwdbcached = pwdb is not None
        self.passworddb = pwdb if pwdb else PasswordDB()
        cli.register(self, self.name, self.description)

        ##################################################################
    def register(self, parser):
        """ Registration function for class. Register with argparse      """
        ##################################################################
        for arg in sorted(self.selected_args):
            parser.add_argument(
                *arguments[arg]['args'],
                **arguments[arg]['kwargs'])

        ##################################################################
    def run(self, parsedargs):
        """ Passes the argparse Namespace object of parsed arguments   """
        ##################################################################
        self._run_command_setup(parsedargs)
        self._run_command_execution()

        ##################################################################
    def _run_command_setup(self, parsedargs):
        """ Passes the argparse Namespace object of parsed arguments   """
        ##################################################################
        self.args = collect_args(parsedargs)
        self._validate_combinatorial_args()
        self._validate_args()
        verify_on_load = self.args['subparser_name'] in ['listrecipients', 'import', 'interpreter']

        # Build the list of recipients that this command will act on
        self._build_recipient_list()

        # If there are defined repositories of keys and certificates, load them
        if not self.iddbcached or self.args['no_cache']:
            self.identities.cabundle = self.args['cabundle']
            self.identities.load_certs_from_directory(
                self.args['certpath'],
                verify_on_load=verify_on_load,
                connectmap=self.args['connect'],
                nocache=self.args['no_cache']
            )
            if self.args['keypath']:
                self.identities.load_keys_from_directory(self.args['keypath'])
            self._validate_identities()

        if self.args['subparser_name'] in ['list', 'interpreter', 'distribute', 'export'] and not self.pwdbcached:
            self.passworddb.load_from_directory(self.args['pwstore'])
        if 'pwname' in self.args and self.args['pwname']:
            self._resolve_directory_path()
        self.args['card_slot'] = self.args['card_slot'] if self.args['card_slot'] else 0
        if 'nopassphrase' in self.selected_args and not self.args['nopassphrase']:
            if self.args['verbosity'] != -1:
                print_card_info(self.args['card_slot'],
                                self.identities.iddb[self.args['identity']],
                                self.args['verbosity'],
                                self.args['color'],
                                self.args['theme_map'])
            self.passphrase = getpass.getpass("Enter Pin/Passphrase: ")

        ####################################################################
    def _resolve_directory_path(self):
        """This handles how a user inputs the pwname, this tries to be smart
        good luck everybody else"""
        ####################################################################
        pwd = getcwd()
        pwd_pwname = path.normpath(path.join(pwd, self.args['pwname']))
        if self.args['pwstore'] in pwd_pwname:
            self.args['pwname'] = pwd_pwname.replace(self.args['pwstore'] + sep, '')

        ##################################################################
    def safety_check(self):
        """ This provides a sanity check that you are the owner of a password."""
        ##################################################################
        try:
            password = PasswordEntry()
            password.read_password_data(path.join(self.args['pwstore'], self.args['pwname']))
            return (self.args['identity'] in password['recipients'].keys(), password['metadata']['creator'])
        except PasswordIOError:
            return (True, None)

        ##################################################################
    def update_pass(self, pass_value):
        """Fully updated a password record"""
        ##################################################################
        pass_entry = PasswordEntry()
        pass_entry.read_password_data(path.join(self.args['pwstore'], self.args['pwname']))
        swap_pass = PasswordEntry()
        swap_pass.add_recipients(secret=pass_value,
                                 distributor=self.args['identity'],
                                 recipients=[self.args['identity']],
                                 identitydb=self.identities,
                                 passphrase=self.passphrase,
                                 card_slot=self.args['card_slot'],
                                 pwstore=self.args['pwstore']
                                )
        pass_entry['recipients'][self.args['identity']] = swap_pass['recipients'][self.args['identity']]
        pass_entry.write_password_data(path.join(self.args['pwstore'], self.args['pwname']),
                                       overwrite=self.args['overwrite'])

        ##################################################################
    def create_pass(self, password1, description, authorizer, recipient_list=None):
        """ This writes password data to a file."""
        ##################################################################
        password_metadata = {}
        password_metadata['description'] = description
        password_metadata['authorizer'] = authorizer
        password_metadata['creator'] = self.args['identity']
        password_metadata['name'] = self.args['pwname']
        if self.args['noescrow']:
            self.args['min_escrow'] = None
            self.args['escrow_users'] = None
        if recipient_list is None:
            recipient_list = [self.args['identity']]

        password = PasswordEntry(**password_metadata)

        password.add_recipients(secret=password1,
                                distributor=self.args['identity'],
                                recipients=recipient_list,
                                identitydb=self.identities,
                                passphrase=self.passphrase,
                                card_slot=self.args['card_slot'],
                                escrow_users=self.args['escrow_users'],
                                minimum=self.args['min_escrow'],
                                pwstore=self.args['pwstore']
                               )

        password.write_password_data(path.join(self.args['pwstore'], self.args['pwname']),
                                     overwrite=self.args['overwrite'])

        ##################################################################
    def create_or_update_pass(self, password1, description, authorizer, recipient_list=None):
        """ This creates new or updates existing passwords """
        ##################################################################
        safe, owner = self.safety_check()
        if safe or self.args['overwrite']:
            if owner and owner != self.args['identity']:
                self.update_pass(password1)
            else:
                self.create_pass(password1, description, authorizer, recipient_list)
        else:
            raise NotThePasswordOwnerError(self.args['identity'], owner, self.args['pwname'])

        ##################################################################
    def delete_pass(self):
        """This deletes a password that the user has created, useful for testing"""
        ##################################################################
        filepath = path.join(self.args['pwstore'], self.args['pwname'])
        try:
            remove(filepath)
        except OSError as err:
            raise PasswordIOError("Password '%s' not found" % self.args['pwname']) from err

        ##################################################################
    def rename_pass(self):
        """This renames a password that the user has created"""
        ##################################################################
        oldpath = path.join(self.args['pwstore'], self.args['pwname'])
        newpath = path.join(self.args['pwstore'], self.args['rename'])
        try:
            rename(oldpath, newpath)
            password = PasswordEntry()
            password.read_password_data(newpath)
            password['metadata']['name'] = self.args['rename']
            password.write_password_data(newpath)

        except OSError as err:
            raise PasswordIOError("Password '%s' not found" % self.args['pwname']) from err

        ##################################################################
    def _run_command_execution(self):
        """ Passes the argparse Namespace object of parsed arguments   """
        ##################################################################
        raise NotImplementedError

        ##################################################################
    def _build_recipient_list(self):
        """take groups and users and make a SOA for the recipients"""
        ##################################################################
        try:
            if 'groups' in self.args and self.args['groups']:
                self.recipient_list += self._parse_group_membership()
            if 'users' in self.args and self.args['users']:
                self.recipient_list += self.args['users']
            self.recipient_list = [x.strip() for x in list(set(self.recipient_list))]
            self.escrow_and_recipient_list = self.recipient_list + self.args['escrow_users']
            for user in self.escrow_and_recipient_list:
                if str(user) == '':
                    raise NullRecipientError
        except KeyError:  # If this is a command with no users, don't worry about it
            pass

        ##################################################################
    def _parse_group_membership(self):
        """Concat membership of supplied groups"""
        ##################################################################
        member_list = []
        try:
            for group in self.args['groups']:
                member_list += [user.strip() for user in self.args[group.strip()].split(",") if user.strip()]
            return member_list
        except KeyError as err:
            raise GroupDefinitionError(str(err)) from err

        ##################################################################
    def _validate_args(self):
        ##################################################################
        raise NotImplementedError

        ##################################################################
    def _validate_combinatorial_args(self):
        """ This is a weird function name so: combinatorial in this case
            means that one of the 'combinatorial' arguments are required
            however, not all of them are necessarily required.
            Ex: We need certs, we can get this from certpath or connect
            we do not need both of these arguments but at least one is
            required"""
        ##################################################################
        # we want a multi-dim of lists, this way if more combinations come up
        # that would be required in a 1 or more capacity, we just add
        # a list to this list
        args_list = [['certpath', 'connect']]
        for arg_set in args_list:
            valid = False
            for arg in arg_set:
                if arg in self.args and self.args[arg] is not None:
                    valid = True
                    break
            if not valid:
                raise CliArgumentError(
                    "'%s' or '%s' is required" % tuple(arg_set))

        ##################################################################
    def _validate_identities(self, swap_list=None):
        """Ensure identities meet criteria for processing"""
        ##################################################################
        if not swap_list:
            swap_list = self.escrow_and_recipient_list
        for recipient in swap_list:
            self.identities.verify_identity(recipient, [])
            if recipient not in self.identities.iddb.keys():
                raise CliArgumentError(
                    "Error: Recipient '%s' is not in the recipient database" %
                    recipient)

        if self.args['identity'] in self.identities.iddb.keys():
            self.identities.verify_identity(self.args['identity'], [])
        else:
            raise CliArgumentError(
                "Error: Your user '%s' is not in the recipient database" %
                self.args['identity'])

        ##################################################################
    def _print_debug(self):
        ##################################################################
        print(self.recipient_list)
        print(self.identities.iddb.keys())

        ##################################################################
    def color_print(self, string, color_type):
        """Handle the color printing for objects"""
        ##################################################################
        return color_prepare(string, color_type,
                             self.args['color'],
                             self.args['theme_map'])

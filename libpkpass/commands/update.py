"""This module allows for the updating of passwords"""
import getpass
from os import path
from libpkpass.util import sort
from libpkpass.password import PasswordEntry
from libpkpass.commands.command import Command
from libpkpass.errors import CliArgumentError, PasswordMismatchError, NotThePasswordOwnerError,\
        BlankPasswordError

    ####################################################################
class Update(Command):
    """This class implements the CLI functionality of updating existing passwords"""
    ####################################################################
    name = 'update'
    description = 'Change a password value and redistribute to recipients'
    selected_args = Command.selected_args + ['pwname', 'pwstore', 'overwrite', 'stdin', 'keypath',
                                             'nopassphrase', 'nosign', 'card_slot', 'escrow_users',
                                             'min_escrow', 'noescrow']

        ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                      """
        ####################################################################
        password = PasswordEntry()
        password.read_password_data(path.join(
            self.args['pwstore'], self.args['pwname']))
        safe, owner = self.safety_check()
        if safe or self.args['overwrite']:
            self.recipient_list = password['recipients'].keys()
            print("The following list of users are the current distribution list:")
            print(", ".join(sort(self.recipient_list)))
            correct_distribution = input("Is this list correct? (y/N) ")
            if not correct_distribution or correct_distribution.lower()[0] == 'n':
                self._new_distribution()

            self._validate_identities(self.recipient_list)

            password1 = getpass.getpass("Enter updated password: ")
            if password1.strip() == "":
                raise BlankPasswordError
            password2 = getpass.getpass("Enter updated password again: ")
            if password1 != password2:
                raise PasswordMismatchError

            # This is due to a poor naming convention; we don't want to go through the
            # create or update, because we are not updating a single record in the yaml
            # we are burning it to the ground and redoing the entire thing
            self.create_pass(password1,
                             password['metadata']['description'],
                             password['metadata']['authorizer'],
                             self.recipient_list)
        else:
            raise NotThePasswordOwnerError(self.args['identity'], owner, self.args['pwname'])

        ####################################################################
    def _new_distribution(self):
        """enter a new recipient list"""
        ####################################################################
        breaker = False
        while not breaker:
            self.recipient_list = input("Please enter a comma delimited list: ")
            self.recipient_list = list({x.strip() for x in self.recipient_list.split(",")})
            print(self.recipient_list)
            try:
                self._validate_identities(self.recipient_list)
                breaker = True
            except CliArgumentError as err:
                print(err)
                continue

        ####################################################################
    def _validate_args(self):
        ####################################################################
        for argument in ['pwname', 'keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(f"'{argument}' is a required argument")

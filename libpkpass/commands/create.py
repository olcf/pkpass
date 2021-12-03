"""This module allows for the creation of passwords"""
import getpass
from sys import stdin
from libpkpass.commands.command import Command
from libpkpass.errors import CliArgumentError, PasswordMismatchError, BlankPasswordError

    ####################################################################
class Create(Command):
    """This class implements the CLI functionality of creation of passwords"""
    ####################################################################
    name = 'create'
    description = 'Create a new password entry and encrypt it for yourself'
    selected_args = Command.selected_args + ['pwname', 'pwstore', 'overwrite', 'stdin', 'keypath',
                                             'nopassphrase', 'nosign', 'card_slot', 'escrow_users',
                                             'min_escrow', 'noescrow', 'description', 'authorizer']

        ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                      """
        ####################################################################

        if not self.args['stdin']:
            password1 = getpass.getpass("Enter password to create: ")
            if password1.strip() == "":
                raise BlankPasswordError
            password2 = getpass.getpass("Enter password to create again: ")
            if password1 != password2:
                raise PasswordMismatchError
        else:
            password1 = stdin.read()

        if 'description' not in self.args or not self.args['description']:
            self.args['description'] = input("Description: ")

        if 'authorizer' not in self.args or not self.args['authorizer']:
            self.args['authorizer'] = input("Authorizer: ")

        self.create_or_update_pass(password1, self.args['description'], self.args['authorizer'])
        ####################################################################
    def _validate_args(self):
        ####################################################################
        for argument in ['pwname', 'keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(f"'{argument}' is a required argument")

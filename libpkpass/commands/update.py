"""This module allows for the updating of passwords"""

from __future__ import print_function
import getpass
import os
from builtins import input
from libpkpass.password import PasswordEntry
from libpkpass.commands.command import Command
from libpkpass.errors import CliArgumentError, PasswordMismatchError, NotThePasswordOwnerError,\
        BlankPasswordError

def sort(lst):
    """Sort our alphanumeric keys"""
    lst = [str(i) for i in lst]
    lst.sort()
    return [int(i) if i.isdigit() else i for i in lst]

class Update(Command):
    """This class implements the CLI functionality of updating existing passwords"""
    name = 'update'
    description = 'Change a password value and redistribute to recipients'
    selected_args = ['pwname', 'pwstore', 'overwrite', 'stdin', 'identity', 'certpath',
                     'keypath', 'cabundle', 'nopassphrase', 'nosign', 'card_slot',
                     'escrow_users', 'min_escrow', 'noescrow']

    def _run_command_execution(self):
        ####################################################################
        """ Run function for class.                                      """
        ####################################################################
        password = PasswordEntry()
        password.read_password_data(os.path.join(
            self.args['pwstore'], self.args['pwname']))
        safe, owner = self.safety_check()
        if safe or self.args['overwrite']:
            self.recipient_list = password['recipients'].keys()
            print("The following list of users are the current distribution list:")
            print(", ".join(sort(self.recipient_list)))
            correct_distribution = input("Is this list correct? (y/N) ")
            if not correct_distribution or correct_distribution.lower()[0] == 'n':
                self.recipient_list = input("Please enter a comma delimited list: ")
                self.recipient_list = list(set(self._convert_strings_to_list(self.recipient_list)))
                print(self.recipient_list)

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


    def _validate_args(self):
        for argument in ['pwname', 'keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)

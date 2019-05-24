"""This module allows for the creation of passwords"""
from __future__ import print_function
import os
import sys
from builtins import input
from libpkpass.commands.command import Command
from libpkpass.password import PasswordEntry
from libpkpass.errors import CliArgumentError, NotThePasswordOwnerError


class Delete(Command):
    """This class implements the CLI functionality of deletion of passwords"""
    name = 'delete'
    description = 'Delete a password in the repository'
    selected_args = ['pwname', 'pwstore', 'overwrite', 'stdin', 'identity', 'certpath', 'nopassphrase',
                     'keypath', 'cabundle', 'card_slot']

    def _run_command_execution(self):
        ####################################################################
        """ Run function for class.                                      """
        ####################################################################
        safe, owner = self.safety_check()
        if safe or self.args['overwrite']:
            myidentity = self.identities.iddb[self.args['identity']]
            password = PasswordEntry()
            password.read_password_data(os.path.join(self.args['pwstore'], self.args['pwname']))
            plaintext_pw = password.decrypt_entry(
                identity=myidentity, passphrase=self.passphrase, card_slot=self.args['card_slot'])
            self._confirmation(plaintext_pw)
        else:
            raise NotThePasswordOwnerError(self.args['identity'], owner)


    def _confirmation(self, plaintext_pw):
        yes = {'yes', 'y', 'ye', ''}
        deny = {'no', 'n'}
        confirmation = input("%s: %s\nDelete this password?(Defaults yes):"
                             % (self.args['pwname'], plaintext_pw))
        if confirmation.lower() in yes:
            self.delete_pass()
        elif confirmation.lower() in deny:
            sys.exit()
        else:
            print("please respond with yes or no")
            self._confirmation(plaintext_pw)

    def _validate_args(self):
        for argument in ['pwname', 'keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)

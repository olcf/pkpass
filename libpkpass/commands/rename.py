"""This module allows for the renaming of passwords"""
import os
import sys
from libpkpass.commands.command import Command
from libpkpass.password import PasswordEntry
from libpkpass.errors import CliArgumentError, NotThePasswordOwnerError

    ####################################################################
class Rename(Command):
    """This class implements the CLI functionality of renaming of passwords"""
    ####################################################################
    name = 'rename'
    description = 'Rename a password in the repository'
    selected_args = Command.selected_args + ['pwname', 'pwstore', 'overwrite', 'stdin', 'nopassphrase',
                                             'keypath', 'card_slot', 'rename']

        ####################################################################
    def _run_command_execution(self):
        """ Run function for class. """
        ####################################################################
        safe, owner = self.safety_check()
        if safe and owner:
            orig_pass = self.args['pwname']
            self.args['pwname'] = self.args['rename']
            resafe, reowner = self.safety_check()
            self.args['pwname'] = orig_pass
            if resafe or self.args['overwrite']:
                password = PasswordEntry()
                password.read_password_data(os.path.join(self.args['pwstore'], self.args['pwname']))
                plaintext_pw = password.decrypt_entry(
                    identity=self.identity, passphrase=self.passphrase, card_slot=self.args['card_slot'])
                self._confirmation(plaintext_pw)
            else:
                raise NotThePasswordOwnerError(self.args['identity'], reowner, self.args['rename'])
        else:
            raise NotThePasswordOwnerError(self.args['identity'], owner, self.args['pwname'])

        ####################################################################
    def _confirmation(self, plaintext_pw):
        """Run confirmation for rename"""
        ####################################################################
        yes = {'yes', 'y', 'ye', ''}
        deny = {'no', 'n'}
        confirmation = input(f"{self.args['pwname']}: {plaintext_pw}\nRename this password?(Defaults yes): ")
        if confirmation.lower() in yes:
            self.rename_pass()
        elif confirmation.lower() in deny:
            sys.exit()
        else:
            print("please respond with yes or no")
            self._confirmation(plaintext_pw)

        ####################################################################
    def _validate_args(self):
        """Validate necessary arguments"""
        ####################################################################
        for argument in ['pwname', 'keypath', 'rename']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(f"'{argument}' is a required argument")

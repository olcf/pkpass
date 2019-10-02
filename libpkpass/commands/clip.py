"""This Module allows for copying a password directly to the clipboard"""

from __future__ import print_function
import time
import os
import pyperclip
from libpkpass.commands.command import Command
from libpkpass.password import PasswordEntry
from libpkpass.errors import CliArgumentError


class Clip(Command):
    """This class allows for the copying of a password to the clipboard"""
    name = 'clip'
    description = 'Copy a password to clipboard'
    selected_args = Command.selected_args + ['pwname', 'pwstore', 'stdin', 'time', 'keypath',
                                             'nopassphrase', 'noverify', 'card_slot']

    def _run_command_execution(self):
        ####################################################################
        """ Run function for class.                                      """
        ####################################################################

        password = PasswordEntry()
        password.read_password_data(os.path.join(
            self.args['pwstore'], self.args['pwname']))
        myidentity = self.identities.iddb[self.args['identity']]

        plaintext_pw = password.decrypt_entry(
            identity=myidentity,
            passphrase=self.passphrase,
            card_slot=self.args["card_slot"])

        if not self.args['noverify']:
            result = password.verify_entry(
                myidentity['uid'], self.identities)
            if not result['sigOK']:
                print("Warning:  Could not verify that '%s' correctly signed your password entry." %
                      result['distributor'])
            if not result['certOK']:
                print("Warning:  Could not verify the certificate authenticity of user '%s'." %
                      result['distributor'])

        oldclip = pyperclip.paste()
        try:
            pyperclip.copy(plaintext_pw)
            print("Password copied into paste buffer for %s seconds" %
                  self.args['time'])
            time.sleep(self.args['time'])
        finally:
            pyperclip.copy(oldclip)

    def _validate_args(self):
        for argument in ['keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)

"""This Module allows for copying a password directly to the clipboard"""
from time import sleep
from os import path
from pyperclip import copy, paste
from libpkpass import LOGGER
from libpkpass.commands.command import Command
from libpkpass.password import PasswordEntry
from libpkpass.errors import CliArgumentError
from libpkpass.models.recipient import Recipient

    ####################################################################
class Clip(Command):
    """This class allows for the copying of a password to the clipboard"""
    ####################################################################
    name = 'clip'
    description = 'Copy a password to clipboard'
    selected_args = Command.selected_args + ['pwname', 'pwstore', 'stdin', 'time', 'keypath',
                                             'nopassphrase', 'noverify', 'card_slot']

        ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                      """
        ####################################################################
        password = PasswordEntry()
        password.read_password_data(path.join(
            self.args['pwstore'], self.args['pwname']))
        distributor = password.recipients[self.identity['name']]['distributor']

        plaintext_pw = password.decrypt_entry(
            identity=self.identity,
            passphrase=self.passphrase,
            card_slot=self.args["card_slot"])

        if not self.args['noverify']:
            result = password.verify_entry(
                self.identity['name'],
                self.identities,
                distributor,
                self.session.query(Recipient).filter(Recipient.name==distributor).first().certs,
            )
            if not result['sigOK']:
                LOGGER.warning(
                    "Could not verify that %s correctly signed your password entry.",
                    result['distributor']
                )
            if not result['certOK']:
                LOGGER.warning(
                    "Could not verify the certificate authenticity of user '%s'.",
                    result['distributor']
                )

        oldclip = paste()
        try:
            copy(plaintext_pw)
            yield f"Password copied into paste buffer for {self.args['time']} seconds"
            sleep(self.args['time'])
        finally:
            copy(oldclip)

        ####################################################################
    def _validate_args(self):
        ####################################################################
        for argument in ['keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(f"'{argument}' is a required argument")

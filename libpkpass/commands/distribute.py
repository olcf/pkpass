"""This Modules allows for distributing created passwords to other users"""
import os
from libpkpass.commands.command import Command
from libpkpass.password import PasswordEntry
from libpkpass.errors import CliArgumentError


class Distribute(Command):
    """This Class implements the CLI functionality for ditribution"""
    name = 'distribute'
    description = 'Distribute an existing password entry to another entity'
    selected_args = ['pwname', 'pwstore', 'users', 'groups', 'stdin', 'identity',
                     'certpath', 'cabundle', 'keypath', 'nopassphrase', 'noverify', 'nosign', 'card_slot']

    def _run_command_execution(self):
        ####################################################################
        """ Run function for class.                                      """
        ####################################################################

        password = PasswordEntry()
        password.read_password_data(os.path.join(
            self.args['pwstore'], self.args['pwname']))
        plaintext_pw = password.decrypt_entry(
            self.identities.iddb[self.args['identity']],
            passphrase=self.passphrase)

        password.add_recipients(secret=plaintext_pw,
                                distributor=self.args['identity'],
                                recipients=self.recipient_list,
                                identitydb=self.identities,
                                passphrase=self.passphrase,
                                card_slot=self.args["card_slot"]
                               )

        password.write_password_data(os.path.join(
            self.args['pwstore'], self.args['pwname']))

    def _validate_args(self):
        for argument in ['certpath', 'keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)

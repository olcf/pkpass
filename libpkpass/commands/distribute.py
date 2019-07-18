"""This Modules allows for distributing created passwords to other users"""
import os
from libpkpass.commands.command import Command
from libpkpass.password import PasswordEntry
from libpkpass.errors import CliArgumentError


class Distribute(Command):
    """This Class implements the CLI functionality for ditribution"""
    name = 'distribute'
    description = 'Distribute an existing password entry to another entity'
    selected_args = ['pwname', 'pwstore', 'users', 'groups', 'stdin', 'identity', 'min_escrow', 'escrow_users',
                     'certpath', 'cabundle', 'keypath', 'nopassphrase', 'nosign', 'card_slot',
                     'noescrow']

    def _run_command_execution(self):
        ####################################################################
        """ Run function for class.                                      """
        ####################################################################

        password = PasswordEntry()
        password.read_password_data(os.path.join(
            self.args['pwstore'], self.args['pwname']))
        # we shouldn't modify escrow on distribute
        self.args['min_escrow'] = None
        self.args['escrow_users'] = None
        plaintext_pw = password.decrypt_entry(
            self.identities.iddb[self.args['identity']],
            passphrase=self.passphrase,
            card_slot=self.args['card_slot'])

        password.add_recipients(secret=plaintext_pw,
                                distributor=self.args['identity'],
                                recipients=self.recipient_list,
                                identitydb=self.identities,
                                passphrase=self.passphrase,
                                card_slot=self.args['card_slot'],
                                pwstore=self.args['pwstore']
                               )

        password.write_password_data(os.path.join(
            self.args['pwstore'], self.args['pwname']))

    def _validate_args(self):
        for argument in ['pwname', 'keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)

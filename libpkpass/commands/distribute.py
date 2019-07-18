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
        if self.args['noescrow']:
            self.args['min_escrow'] = None
            self.args['escrow_users'] = None
        else:
            escrow_map = password.read_escrow(self.args['pwname'])
            # needless computation if escrow already exists. password only changes on create
            # and create will wipe escrow users; so distribute only needs to happen if the
            # users do not already exist in a group
            for _, value in escrow_map.items():
                if set(value['recipients'].keys()) == set(self.args['escrow_users']):
                    self.args['escrow_users'] = None
                    self.args['min_escrow'] = 0
                    break
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
                                minimum=self.args['min_escrow'],
                                escrow_users=self.args['escrow_users'],
                                pwstore=self.args['pwstore']
                               )

        password.write_password_data(os.path.join(
            self.args['pwstore'], self.args['pwname']))

    def _validate_args(self):
        for argument in ['pwname', 'keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)

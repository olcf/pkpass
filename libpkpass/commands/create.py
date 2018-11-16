"""This module allows for the creation of passwords"""
import getpass
import os
from libpkpass.commands.command import Command
from libpkpass.password import PasswordEntry
from libpkpass.errors import CliArgumentError, PasswordMismatchError


class Create(Command):
    """This class implements the CLI functionality of creation of passwords"""
    name = 'create'
    description = 'Create a new password entry and encrypt it for yourself'
    selected_args = ['pwname', 'pwstore', 'overwrite', 'stdin', 'identity', 'certpath',
                     'keypath', 'cabundle', 'nopassphrase', 'noverify', 'nosign', 'card_slot',
                     'escrow_users', 'min_escrow']

    def _run_command_execution(self):
        ####################################################################
        """ Run function for class.                                      """
        ####################################################################
        password1 = getpass.getpass("Enter password to create: ")
        password2 = getpass.getpass("Enter password to create again: ")
        if password1 != password2:
            raise PasswordMismatchError

        password_metadata = {}
        for item in ['Description', 'Authorizer']:
            password_metadata[item.lower()] = raw_input("%s: " % item)
        password_metadata['creator'] = self.args['identity']
        password_metadata['name'] = self.args['pwname']

        password = PasswordEntry(**password_metadata)

        password.add_recipients(secret=password1,
                                distributor=self.args['identity'],
                                recipients=[self.args['identity']],
                                identitydb=self.identities,
                                passphrase=self.passphrase,
                                card_slot=self.args["card_slot"]
                               )

        password.write_password_data(os.path.join(
            self.args['pwstore'], self.args['pwname']), overwrite=self.args['overwrite'])

    def _validate_args(self):
        for argument in ['pwname', 'certpath', 'keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)

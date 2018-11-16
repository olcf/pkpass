"""This module is used to process the decryption of keys"""
import os
from libpkpass.commands.command import Command
from libpkpass.password import PasswordEntry
from libpkpass.errors import PasswordIOError, CliArgumentError, NotARecipientError


class Show(Command):
    """This class is used as a command object and parses information passed through
    the CLI to show passwords that have been distributed to users"""
    name = 'show'
    description = 'Display a password'
    selected_args = ['pwname', 'pwstore', 'stdin', 'identity', 'certpath', 'escrow_users',
                     'keypath', 'cabundle', 'nopassphrase', 'noverify', 'card_slot', 'all',
                     'min_escrow']

    def _run_command_execution(self):
        ####################################################################
        """ Run function for class.                                      """
        ####################################################################

        password = PasswordEntry()
        myidentity = self.identities.iddb[self.args['identity']]

        if self.args['all'] and self.args['pwname'] is None:
            self._walk_dir(self.args['pwstore'], password, myidentity)
        elif self.args['pwname'] is None:
            raise PasswordIOError("No password supplied")
        else:
            self._decrypt_password_entry(
                self.args['pwstore'], password, myidentity, self.args['pwname'])

    def _validate_args(self):
        for argument in ['certpath', 'keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)

    def _walk_dir(self, directory, password, myidentity):
        # os.walk returns root, dirs, and files we just need files
        for root, _, pwnames in os.walk(directory):
            for pwname in pwnames:
                password.read_password_data(os.path.join(root, pwname))
                try:
                    self._decrypt_password_entry(
                        root, password, myidentity, pwname)
                except NotARecipientError:
                    continue
        return

    def _decrypt_password_entry(self, directory, password, myidentity, pwname):
        """This decrypts a given password entry"""
        password.read_password_data(os.path.join(directory, pwname))
        plaintext_pw = password.decrypt_entry(
            identity=myidentity, passphrase=self.passphrase, card_slot=self.args['card_slot'])
        if not self.args['noverify']:
            result = password.verify_entry(
                myidentity['uid'], self.identities.iddb)
            if not result['sigOK']:
                print("warning: could not verify that '%s' correctly signed your password entry." %
                      result['distributor'])
            if not result['certOK']:
                print("Warning: could not verify the certificate authenticity of user '%s'." %
                      result['distributor'])

        print("%s: %s") % (password.metadata['name'], plaintext_pw)

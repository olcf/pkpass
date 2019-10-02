"""This module is used to process the decryption of keys"""

from __future__ import print_function
import os
from libpkpass.commands.command import Command
from libpkpass.password import PasswordEntry
from libpkpass.errors import PasswordIOError, CliArgumentError, NotARecipientError, DecryptionError


class Show(Command):
    """This class is used as a command object and parses information passed through
    the CLI to show passwords that have been distributed to users"""
    name = 'show'
    description = 'Display a password'
    selected_args = Command.selected_args + ['pwname', 'pwstore', 'stdin', 'keypath', 'nopassphrase',
                                             'noverify', 'card_slot', 'all', 'recovery', 'ignore_decrypt']

    def _run_command_execution(self):
        ####################################################################
        """ Run function for class.                                      """
        ####################################################################

        password = PasswordEntry()
        myidentity = self.identities.iddb[self.args['identity']]

        if self.args['all']:
            try:
                self._walk_dir(self.args['pwstore'], password, myidentity, self.args['ignore_decrypt'])
            except DecryptionError as err:
                raise err
        elif self.args['pwname'] is None:
            raise PasswordIOError("No password supplied")
        else:
            self._decrypt_wrapper(
                self.args['pwstore'], password, myidentity, self.args['pwname'])

    def _walk_dir(self, directory, password, myidentity, ignore_decrypt=False):
        # os.walk returns root, dirs, and files we just need files
        for root, _, pwnames in os.walk(directory):
            for pwname in pwnames:
                if self.args['pwname'] is None or self.args['pwname'].upper() in pwname.upper():
                    try:
                        self._decrypt_wrapper(
                            root, password, myidentity, pwname)
                    except DecryptionError as err:
                        if ignore_decrypt:
                            print(err.msg)
                            continue
                        raise
                    except NotARecipientError:
                        continue

    def _handle_escrow_show(self, password, myidentity):
        ####################################################################
        """This populates the user's escrow as passwords"""
        ####################################################################
        myescrow = []
        if password.escrow:
            for key, value in password['escrow'].items():
                if myidentity['uid'] in value['recipients'].keys():
                    myescrow.append([value['recipients'][myidentity['uid']], key])
        return myescrow

    def _decrypt_wrapper(self, directory, password, myidentity, pwname):
        password.read_password_data(os.path.join(directory, pwname))
        myescrow = []
        if self.args['recovery']:
            myescrow = self._handle_escrow_show(password, myidentity)
        if myescrow:
            for share in myescrow:
                password['recipients'][myidentity['uid']] = share[0]
                print("Share for escrow group: %s" % share[1])
                self._decrypt_password_entry(password, myidentity)
        else:
            self._decrypt_password_entry(password, myidentity)

    def _decrypt_password_entry(self, password, myidentity):
        ####################################################################
        """This decrypts a given password entry"""
        ####################################################################
        plaintext_pw = password.decrypt_entry(
            identity=myidentity, passphrase=self.passphrase, card_slot=self.args['card_slot'])
        if not self.args['noverify']:
            result = password.verify_entry(
                myidentity['uid'], self.identities)
            if not result['sigOK']:
                print("warning: could not verify that '%s' correctly signed your password entry." %
                      result['distributor'])
            if not result['certOK']:
                print("Warning: could not verify the certificate authenticity of user '%s'." %
                      result['distributor'])

        print(("%s: %s") % (password.metadata['name'], plaintext_pw))

    def _validate_args(self):
        for argument in ['keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)

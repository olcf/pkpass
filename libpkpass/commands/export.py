"""This Module allows for the export of passwords for the purpose of importing to a new card"""
import os
from libpkpass.commands.command import Command
from libpkpass.passworddb import PasswordDB
from libpkpass.errors import CliArgumentError


class Export(Command):
    """This Class implements the cli functionality of export"""
    name = 'export'
    description = 'Export passwords that you have access to and encrypt with aes'
    selected_args = ['stdin', 'identity', 'certpath',
                     'cabundle', 'noverify', 'dstpwstore', 'card_slot']

    def _run_command_execution(self):
        ####################################################################
        """ Run function for class.                                      """
        ####################################################################

        passworddb = PasswordDB()
        for path, _, files in os.walk(self.args['pwstore']):
            for passwordname in files:
                passwordpath = os.path.join(path, passwordname)
                passworddb.load_password_data(passwordpath)

        for key, password in passworddb.pwdb.items():
            myrecipiententry = password.recipients[self.args['identity']]
            password.recpients = [myrecipiententry]
            # Decrypt password
            plaintext_pw = password.decrypt_entry(
                identity=myidentity,
                passphrase=self.passphrase,
                card_slot=self.args["card_slot"])
            # Encrypt with passphrase
            sk_encrypt_string(plaintext_pw, key)
            # Replace derived key and encryption algorithm
            print plaintext_pw
            # Write out the password entry

    def _validate_args(self):
        ####################################################################
        """ Ensure arguments are appropriate for this command           """
        ####################################################################
        for argument in ['certpath', 'keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)

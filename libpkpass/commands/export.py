"""This Module allows for the export of passwords for the purpose of importing to a new card"""

from __future__ import print_function
import os
import getpass
from libpkpass.commands.command import Command
from libpkpass.passworddb import PasswordDB
from libpkpass.errors import CliArgumentError, PasswordMismatchError

    ####################################################################
class Export(Command):
    """This Class implements the cli functionality of export"""
    ####################################################################
    name = 'export'
    description = 'Export passwords that you have access to and encrypt with aes'
    selected_args = Command.selected_args + ['pwfile', 'stdin', 'nopassphrase', 'dstpwstore',
                                             'card_slot', 'nocrypto']

        ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                      """
        ####################################################################
        myidentity = self.identities.iddb[self.args['identity']]
        passworddb = PasswordDB()
        crypt_pass = False
        for path, _, files in os.walk(self.args['pwstore']):
            for passwordname in files:
                passwordpath = os.path.join(path, passwordname)
                passworddb.load_password_data(passwordpath)
        if not self.args['nocrypto']:
            crypt_pass = getpass.getpass("Please enter a password for the encryption: ")
            verify_pass = getpass.getpass("Please enter again for verification: ")
            if crypt_pass != verify_pass:
                raise PasswordMismatchError()

        self._iterate_pdb(myidentity, passworddb, crypt_pass)

        ####################################################################
    def _iterate_pdb(self, myidentity, passworddb, crypt_pass=False):
        """ Iterate through the passwords that we can decrypt """
        ####################################################################
        uid = myidentity['uid']
        all_passwords = {k:v for (k, v) in passworddb.pwdb.items() if uid in v.recipients.keys()}
        i = 1
        for _, password in all_passwords.items():
            plaintext_pw = password.decrypt_entry(
                identity=myidentity,
                passphrase=self.passphrase,
                card_slot=self.args["card_slot"])
            password.recipients[uid]['encrypted_secret'] = plaintext_pw.encode("ASCII")
            password.write_password_data(self.args['pwfile'],
                                         overwrite=False,
                                         encrypted_export=not self.args['nocrypto'],
                                         password=crypt_pass,
                                         export=True)
            self.progress_bar(i, len(all_passwords))
            i += 1
        print("")

        ####################################################################
    def _validate_args(self):
        """ Ensure arguments are appropriate for this command           """
        ####################################################################
        for argument in ['pwfile', 'keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)

        ####################################################################
    def _validate_combinatorial_args(self):
        ####################################################################
        pass

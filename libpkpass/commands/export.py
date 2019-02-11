"""This Module allows for the export of passwords for the purpose of importing to a new card"""

from __future__ import print_function
import os
import getpass
from libpkpass.commands.command import Command
from libpkpass.passworddb import PasswordDB
from libpkpass.errors import CliArgumentError, PasswordMismatchError

class Export(Command):
    """This Class implements the cli functionality of export"""
    name = 'export'
    description = 'Export passwords that you have access to and encrypt with aes'
    selected_args = ['pwfile', 'stdin', 'identity', 'certpath', 'nopassphrase',
                     'cabundle', 'noverify', 'dstpwstore', 'card_slot', 'nocrypto']

    def _run_command_execution(self):
        ####################################################################
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

    def _iterate_pdb(self, myidentity, passworddb, crypt_pass=False):
        uid = myidentity['uid']
        db_len = len(passworddb.pwdb.items())
        i = 1
        for _, password in passworddb.pwdb.items():
            plaintext_pw = password.decrypt_entry(
                identity=myidentity,
                passphrase=self.passphrase,
                card_slot=self.args["card_slot"])
            password['recipients'][uid]['encrypted_secret'] = plaintext_pw.encode("ASCII")
            password.write_password_data(self.args['pwfile'], False, not self.args['nocrypto'], crypt_pass)
            self.progress_bar(i, db_len)
            i += 1
        print("")

    def _validate_args(self):
        ####################################################################
        """ Ensure arguments are appropriate for this command           """
        ####################################################################
        for argument in ['pwfile', 'certpath', 'keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)

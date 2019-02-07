"""This Module allows for the export of passwords for the purpose of importing to a new card"""

from __future__ import print_function
import os
import getpass
#import base64
#from cryptography.fernet import Fernet
#from cryptography.hazmat.backends import default_backend
#from cryptography.hazmat.primitives import hashes
#from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
#import libpkpass.crypto as crypto
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
        crypt_pass = None
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


    def _iterate_pdb(self, myidentity, passworddb, crypt_pass=None):
        uid = myidentity['uid']
        for _, password in passworddb.pwdb.items():
            plaintext_pw = password.decrypt_entry(
                identity=myidentity,
                passphrase=self.passphrase,
                card_slot=self.args["card_slot"])
            password['recipients'][uid]['encrypted_secret'] = plaintext_pw.encode("ASCII")
            password.write_password_data(self.args['pwfile'], False, self.args['nocrypto'], crypt_pass)

    def _validate_args(self):
        ####################################################################
        """ Ensure arguments are appropriate for this command           """
        ####################################################################
        for argument in ['pwfile', 'certpath', 'keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)

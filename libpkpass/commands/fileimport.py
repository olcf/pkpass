"""This Module allows for the import of passwords"""

from __future__ import print_function
import getpass
import yaml
import libpkpass.crypto as crypto
from libpkpass.commands.command import Command
from libpkpass.errors import CliArgumentError


class Import(Command):
    """This Class implements the cli functionality of import"""
    name = 'import'
    description = 'Import passwords that you have saved to a file'
    selected_args = ['pwfile', 'stdin', 'identity', 'certpath', 'nopassphrase',
                     'cabundle', 'noverify', 'dstpwstore', 'card_slot', 'nocrypto',]

    def _run_command_execution(self):
        ####################################################################
        """ Run function for class.                                      """
        ####################################################################
        if self.args['nocrypto']:
            self._handle_file(self.args['pwfile'])
        else:
            passwd = getpass.getpass("Please enter the password for the file: ")
            with open(self.args['pwfile'], 'r') as fcontents:
                plaintext = crypto.sk_decrypt_string(fcontents, passwd)
            try:
                self._yaml_file(yaml.safe_load(plaintext))
            except yaml.scanner.ScannerError:
                self._flat_file(plaintext)


    def _handle_file(self, pwfile):
        """This function handles the two expected ways to have password files"""
        try:
            with open(pwfile, 'r') as fname:
                passwords = yaml.safe_load(fname)
            self._yaml_file(passwords)
        except yaml.scanner.ScannerError:
            with open(pwfile, 'r') as fname:
                passwords = fname.readlines()
            self._flat_file(passwords)
        except IOError:
            print("pwfile argument not found: " + self.args['pwfile'])

    def _flat_file(self, passwords):
        """This function handles the simple key:value pair"""
        for password in passwords:
            psplit = password.split(":")
            fname = psplit[0].strip()
            pvalue = psplit[1].strip()
            self.args['pwname'] = fname
            self.args['overwrite'] = False
            self.create_pass(pvalue, "imported", self.args['identity'])

    def _yaml_file(self, passwords):
        """This function handles the yaml format of pkpass"""
        #does not currently work
        for password in passwords:
            print(password)
            #self.create_pass(password, "imported", self.args['identity'])

    def _validate_args(self):
        ####################################################################
        """ Ensure arguments are appropriate for this command           """
        ####################################################################
        for argument in ['pwfile', 'certpath', 'keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)

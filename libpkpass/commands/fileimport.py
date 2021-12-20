"""This Module allows for the import of passwords"""
import getpass
import os.path
from yaml import safe_load, scanner
from tqdm import tqdm
from libpkpass import LOGGER
from libpkpass.crypto import sk_decrypt_string
from libpkpass.commands.command import Command
from libpkpass.password import PasswordEntry
from libpkpass.errors import CliArgumentError, LegacyImportFormatError, FileOpenError

    ####################################################################
class Import(Command):
    """This Class implements the cli functionality of import"""
    ####################################################################
    name = 'import'
    description = 'Import passwords that you have saved to a file'
    selected_args = Command.selected_args + ['pwfile', 'stdin', 'nopassphrase',
                                             'card_slot', 'nocrypto',]

        ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                      """
        ####################################################################
        try:
            contents = ""
            with open(self.args['pwfile'], 'r', encoding='ASCII') as fcontents:
                contents = fcontents.read().strip()
            if self.args['nocrypto']:
                self._file_handler(contents)
            else:
                passwd = getpass.getpass("Please enter the password for the file: ")
                passwords = contents.split("\n")
                for password in tqdm(passwords):
                    self._file_handler(sk_decrypt_string(password, passwd))
        except IOError as err:
            raise FileOpenError(self.args['pwfile'], "No such file or directory") from err

        ####################################################################
    def _file_handler(self, string):
        """This function handles the contents of a file"""
        ####################################################################
        try:
            self._yaml_file(safe_load(string))
        except (TypeError, scanner.ScannerError, KeyError):
            try:
                self._flat_file(string.strip().split("\n"))
            except TypeError as err:
                raise LegacyImportFormatError from err

        ####################################################################
    def _flat_file(self, passwords):
        """This function handles the simple key:value pair"""
        ####################################################################
        LOGGER.info("Flat password file detected, using 'imported' as description \
you can manually change the description in the file if you would like")
        for password in tqdm(passwords):
            psplit = password.split(":")
            fname = psplit[0].strip()
            pvalue = psplit[1].strip()
            self.args['pwname'] = fname
            self.create_or_update_pass(pvalue, "imported", self.args['identity'])

        ####################################################################
    def _yaml_file(self, password):
        """This function handles the yaml format of pkpass"""
        ####################################################################
        uid = self.identity['name']
        pwstore = self.args['pwstore']

        self.args['pwname'] = password['metadata']['name']
        plaintext_str = password['recipients'][uid]['encrypted_secret']
        full_path = os.path.join(pwstore, password['metadata']['name'])
        self.args['overwrite'] = True
        plist = list(password['recipients'])
        if os.path.isfile(full_path):
            existing_password = PasswordEntry()
            existing_password.read_password_data(full_path)
            self.args['overwrite'] = False
            password['metadata'] = existing_password['metadata']
            plist += list(existing_password['recipients'])

        description = password['metadata']['description']
        authorizer = password['metadata']['authorizer']
        self.create_or_update_pass(plaintext_str, description, authorizer, plist)

        ####################################################################
    def _validate_args(self):
        """ Ensure arguments are appropriate for this command           """
        ####################################################################
        for argument in ['pwfile', 'keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(f"'{argument}' is a required argument")

"""This Module allows for the export of passwords for the purpose of importing to a new card"""
import getpass
from tqdm import tqdm
from libpkpass.commands.command import Command
from libpkpass.errors import CliArgumentError, PasswordMismatchError

    ####################################################################
class Export(Command):
    """This Class implements the cli functionality of export"""
    ####################################################################
    name = 'export'
    description = 'Export passwords that you have access to and encrypt with aes'
    selected_args = Command.selected_args + ['pwfile', 'stdin', 'nopassphrase',
                                             'card_slot', 'nocrypto']

        ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                      """
        ####################################################################
        crypt_pass = False
        if not self.args['nocrypto']:
            crypt_pass = getpass.getpass("Please enter a password for the encryption: ")
            verify_pass = getpass.getpass("Please enter again for verification: ")
            if crypt_pass != verify_pass:
                raise PasswordMismatchError()

        self._iterate_pdb(self.passworddb, crypt_pass)

        ####################################################################
    def _iterate_pdb(self, passworddb, crypt_pass=False):
        """ Iterate through the passwords that we can decrypt """
        ####################################################################
        uid = self.identity['name']
        all_passwords = {k:v for (k, v) in passworddb.pwdb.items() if uid in v.recipients.keys()}
        for _, password in tqdm(all_passwords.items()):
            plaintext_pw = password.decrypt_entry(
                identity=self.identity,
                passphrase=self.passphrase,
                card_slot=self.args["card_slot"])
            password.recipients[uid]['encrypted_secret'] = plaintext_pw.encode("UTF-8")
            password.write_password_data(self.args['pwfile'],
                                         overwrite=False,
                                         encrypted_export=not self.args['nocrypto'],
                                         password=crypt_pass,
                                         export=True)

        ####################################################################
    def _validate_args(self):
        """ Ensure arguments are appropriate for this command           """
        ####################################################################
        for argument in ['pwfile', 'keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(f"'{argument}' is a required argument")

        ####################################################################
    def _validate_combinatorial_args(self):
        ####################################################################
        pass

"""This module is used to process the decryption of keys"""
from os import path, unlink, walk
from fnmatch import fnmatch
from tempfile import gettempdir
from libpkpass.commands.command import Command
from libpkpass.password import PasswordEntry
from libpkpass.errors import PasswordIOError, CliArgumentError, NotARecipientError, DecryptionError

    ####################################################################
class Show(Command):
    """This class is used as a command object and parses information passed through
    the CLI to show passwords that have been distributed to users"""
    ####################################################################
    name = 'show'
    description = 'Display a password'
    selected_args = Command.selected_args + [
        'all', 'behalf', 'card_slot', 'ignore_decrypt', 'keypath', 'nopassphrase',
        'noverify', 'pwname', 'pwstore', 'recovery', 'stdin'
    ]
        ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                  """
        ####################################################################
        password = PasswordEntry()
        myidentity = self.identities.iddb[self.args['identity']]
        if 'behalf' in self.args and self.args['behalf']:
            self._behalf_prep(password, myidentity)
        else:
            self._show_wrapper(password, myidentity)

        ####################################################################
    def _show_wrapper(self, password, myidentity):
        """Wrapper for show to allow for on behalf of"""
        ####################################################################
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

        ####################################################################
    def _behalf_prep(self, password, myidentity):
        """Create necessary temporary file for rsa key"""
        ####################################################################
        password.read_password_data(path.join(self.args['pwstore'], self.args['behalf']))
        # allows the password to be stored outside the root of the password directory
        self.args['behalf'] = self.args['behalf'].split('/')[-1]
        temp_key = path.join(gettempdir(), '%s.key' % self.args['behalf'])
        plaintext_pw = password.decrypt_entry(
            identity=myidentity, passphrase=self.passphrase, card_slot=self.args['card_slot'])
        with open(temp_key, 'w') as fname:
            fname.write(
                '%s\n%s\n%s' % (
                    '-----BEGIN RSA PRIVATE KEY-----',
                    plaintext_pw.replace(
                        '-----BEGIN RSA PRIVATE KEY-----', ''
                    ).replace(
                        ' -----END RSA PRIVATE KEY----', ''
                    ).replace(' ', '\n'),
                    '-----END RSA PRIVATE KEY-----'
                )
            )
        self.args['identity'] = self.args['behalf']
        myidentity = self.identities.iddb[self.args['identity']]
        self.args['key_path'] = temp_key
        myidentity['key_path'] = temp_key
        self._show_wrapper(password, myidentity)
        unlink(temp_key)

        ####################################################################
    def _walk_dir(self, directory, password, myidentity, ignore_decrypt=False):
        """Walk our directory searching for passwords"""
        ####################################################################
        # walk returns root, dirs, and files we just need files
        for root, _, pwnames in walk(directory):
            for pwname in pwnames:
                if self.args['pwname'] is None or\
                        fnmatch(path.join(root, pwname), self.args['pwname']):
                    try:
                        self._decrypt_wrapper(
                            root, password, myidentity, pwname)
                    except DecryptionError as err:
                        if ignore_decrypt:
                            print(err)
                            continue
                        raise
                    except NotARecipientError:
                        continue

        ####################################################################
    def _handle_escrow_show(self, password, myidentity):
        """This populates the user's escrow as passwords"""
        ####################################################################
        myescrow = []
        if password.escrow:
            for key, value in password['escrow'].items():
                if myidentity['uid'] in value['recipients'].keys():
                    myescrow.append([value['recipients'][myidentity['uid']], key])
        return myescrow

        ####################################################################
    def _decrypt_wrapper(self, directory, password, myidentity, pwname):
        """Decide whether to decrypt normally or for escrow"""
        ####################################################################
        password.read_password_data(path.join(directory, pwname))
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

        ####################################################################
    def _decrypt_password_entry(self, password, myidentity):
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

        print(("%s: %s") % (self.color_print(password.metadata['name'],
                                             "first_level"), plaintext_pw))

        ####################################################################
    def _validate_args(self):
        ####################################################################
        for argument in ['keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)

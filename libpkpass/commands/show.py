"""This module is used to process the decryption of keys"""
from os import path, unlink, walk
from fnmatch import fnmatch
from tempfile import gettempdir
from libpkpass import LOGGER
from libpkpass.commands.command import Command
from libpkpass.password import PasswordEntry
from libpkpass.errors import PasswordIOError, CliArgumentError, NotARecipientError, DecryptionError
from libpkpass.models.recipient import Recipient

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
        if 'behalf' in self.args and self.args['behalf']:
            yield from self._behalf_prep(password)
        yield from self._show_wrapper(password)

        ####################################################################
    def _show_wrapper(self, password):
        """Wrapper for show to allow for on behalf of"""
        ####################################################################
        if self.args['all']:
            try:
                yield from self._walk_dir(self.args['pwstore'], password, self.args['ignore_decrypt'])
            except DecryptionError as err:
                raise err
        elif self.args['pwname'] is None:
            raise PasswordIOError("No password supplied")
        yield from self._decrypt_wrapper(
            self.args['pwstore'], password, self.args['pwname'])

        ####################################################################
    def _behalf_prep(self, password):
        """Create necessary temporary file for rsa key"""
        ####################################################################
        password.read_password_data(path.join(self.args['pwstore'], self.args['behalf']))
        # allows the password to be stored outside the root of the password directory
        self.args['behalf'] = self.args['behalf'].split('/')[-1]
        temp_key = path.join(gettempdir(), f'{self.args["behalf"]}.key')
        plaintext_pw = password.decrypt_entry(
            identity=self.identity, passphrase=self.passphrase, card_slot=self.args['card_slot'])
        with open(temp_key, 'w', encoding='ASCII') as fname:
            fname.write(
                '%s\n%s\n%s' % (
                    '-----BEGIN RSA PRIVATE KEY-----',
                    plaintext_pw.replace(
                        '-----BEGIN RSA PRIVATE KEY-----', ''
                    ).replace(
                        ' -----END RSA PRIVATE KEY----', ''
                    ).replace(' ', '\n').strip(),
                    '-----END RSA PRIVATE KEY-----'
                )
            )
        self.args['identity'] = self.args['behalf']
        self.args['key_path'] = temp_key
        yield from self._show_wrapper(password)
        unlink(temp_key)

        ####################################################################
    def _walk_dir(self, directory, password, ignore_decrypt=False):
        """Walk our directory searching for passwords"""
        ####################################################################
        # walk returns root, dirs, and files we just need files
        for root, _, pwnames in walk(directory):
            for pwname in pwnames:
                if self.args['pwname'] is None or\
                        fnmatch(path.join(root, pwname), self.args['pwname']):
                    try:
                        yield from self._decrypt_wrapper(
                            root, password, pwname)
                    except DecryptionError as err:
                        if ignore_decrypt:
                            LOGGER.err(err)
                            continue
                        raise
                    except (NotARecipientError, TypeError):
                        continue

        ####################################################################
    def _handle_escrow_show(self, password):
        """This populates the user's escrow as passwords"""
        ####################################################################
        myescrow = []
        if password.escrow:
            for key, value in password['escrow'].items():
                if self.identity in value['recipients'].keys():
                    myescrow.append([value['recipients'][self.identity], key])
        return myescrow

        ####################################################################
    def _decrypt_wrapper(self, directory, password, pwname):
        """Decide whether to decrypt normally or for escrow"""
        ####################################################################
        if directory and password and pwname:
            password.read_password_data(path.join(directory, pwname))
            try:
                distributor = password.recipients[self.identity['name']]['distributor']
                if self.args['recovery']:
                    myescrow = self._handle_escrow_show(password)
                    if myescrow:
                        for share in myescrow:
                            password['recipients'][self.identity['name']] = share[0]
                            yield f"Share for escrow group: {share[1]}"
                            yield self._decrypt_password_entry(password, distributor)
                yield self._decrypt_password_entry(password, distributor)
            except KeyError:
                pass

        ####################################################################
    def _decrypt_password_entry(self, password, distributor):
        """This decrypts a given password entry"""
        ####################################################################
        plaintext_pw = password.decrypt_entry(
            identity=self.identity, passphrase=self.passphrase, card_slot=self.args['card_slot'])
        if not self.args['noverify']:
            result = password.verify_entry(
                self.identity['name'],
                self.identities,
                distributor,
                self.session.query(Recipient).filter(Recipient.name==distributor).first().certs,
            )
            if not result['sigOK']:
                LOGGER.warning(
                    "Could not verify that %s correctly signed your password entry.",
                    result['distributor']
                )
            if not result['certOK']:
                LOGGER.warning(
                    "Could not verify the certificate authenticity of user '%s'.",
                    result['distributor']
                )

        return f"{self.color_print(password.metadata['name'], 'first_level')}: {plaintext_pw}"

        ####################################################################
    def _validate_args(self):
        ####################################################################
        for argument in ['keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(f"'{argument}' is a required argument")

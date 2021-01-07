"""This Module defines what a password contains"""
from uuid import uuid1
from time import time
from datetime import datetime
from os import path, makedirs
from dateutil import parser
import yaml
from tqdm import tqdm
from libpkpass.escrow import pk_split_secret
from libpkpass.errors import NotARecipientError, DecryptionError, PasswordIOError, YamlFormatError,\
    X509CertificateError
import libpkpass.crypto as crypto

    #######################################################################
class PasswordEntry():
    """ Password entry object.  Contains information about a password and
    related metadata, as well as a list of individually encrypted strings"""
    ##########################################################################
    def __init__(self, **kwargs):

        self.metadata = {'name': None,
                         'description': None,
                         'creator': None,
                         'authorizer': None,
                         'signature': None,
                         'schemaVersion': 'v2'}

        self.metadata.update(kwargs)
        self.recipients = {}
        self.escrow = {}

        ####################################################################
    def __getitem__(self, key):
        """Grab items like with dictionaries"""
        ####################################################################
        return getattr(self, key)

        ####################################################################
    def read_escrow(self, filename):
        """Read values from escrow section"""
        ####################################################################
        try:
            with open(filename, 'r') as fname:
                password_data = yaml.safe_load(fname)
                if 'escrow' in password_data.keys():
                    return password_data['escrow']
                return {}
        except (OSError, IOError, yaml.scanner.ScannerError, yaml.parser.ParserError):
            #we actually don't care here.. file might not exist yet
            return {}

        #######################################################################
    def process_escrow_map(
            self,
            escrow_map,
            split_secret=None,
            distributor=None,
            recipients=None,
            identitydb=None,
            encryption_algorithm='rsautl',
            passphrase=None,
            card_slot=None,
            escrow_users=None,
            minimum=None):
        """Process the escrow user map into escrow users"""
        #######################################################################
        escrow_guid = str(uuid1()).replace('-', '')
        if escrow_map:
            for key, value in escrow_map.items():
                if set(value['recipients']) == set(escrow_users):
                    escrow_guid = key
        self.escrow[escrow_guid] = {
            'metadata': {
                'minimum_escrow': minimum,
                'creator': distributor
                },
            'recipients':{}
            }
        i = 0
        for escrow_user in escrow_users:
            if escrow_user not in recipients:
                self.escrow[escrow_guid]['recipients'][escrow_user] = self._add_recipient(
                    escrow_user, split_secret[i], distributor,
                    identitydb, encryption_algorithm, passphrase, card_slot)
                i += 1


        #######################################################################
    def add_escrow(
            self,
            secret=None,
            escrow_users=None,
            minimum=None,
            pwstore=None):
        """ Add escrow users to the recipient list of this password object"""
        #######################################################################
        split_secret = pk_split_secret(secret, escrow_users, minimum)
        return (self.read_escrow(path.join(pwstore, self.metadata['name'])), split_secret)

        #######################################################################
    def add_recipients(
            self,
            secret=None,
            distributor=None,
            recipients=None,
            identitydb=None,
            encryption_algorithm='rsautl',
            passphrase=None,
            card_slot=None,
            escrow_users=None,
            minimum=None,
            pwstore=None):
        """ Add recipients to the recipient list of this password object"""
        #######################################################################
        if recipients is None:
            recipients = []

        new_recipients = {r:self._add_recipient(
            r, secret, distributor, identitydb, encryption_algorithm, passphrase, card_slot
        ) for r in tqdm(recipients, leave=False)}
        self.recipients.update(new_recipients)
        if escrow_users:
            #escrow_users may now be none after the set operations
            try:
                if (len(escrow_users) > 3) and (len(list((set(escrow_users) - set(recipients)))) < 3):
                    print("warning: min_escrow requirement not met after removing password recipients from escrow user list")
                    return
                escrow_map, split_secret = self.add_escrow(
                    secret=secret,
                    escrow_users=escrow_users,
                    minimum=minimum,
                    pwstore=pwstore)
                self.process_escrow_map(
                    escrow_map,
                    split_secret=split_secret,
                    distributor=distributor,
                    recipients=recipients,
                    identitydb=identitydb,
                    encryption_algorithm=encryption_algorithm,
                    passphrase=passphrase,
                    card_slot=card_slot,
                    escrow_users=escrow_users,
                    minimum=minimum)
            except ValueError as err:
                print("Warning cannot create escrow shares, reason: %s" % err)
                print("Your password has been created without escrow capabilities")


        #######################################################################
    def _add_recipient(
            self,
            recipient,
            secret=None,
            distributor=None,
            identitydb=None,
            encryption_algorithm='rsautl',
            passphrase=None,
            card_slot=None,
    ):
        """Add recipient or sharer to list"""
        #######################################################################
        try:
            encrypted_secrets = {}
            for cert in identitydb.iddb[recipient]['certs']:
                if encryption_algorithm == 'rsautl':
                    if 'key_path' in identitydb.iddb[recipient].keys():
                        (encrypted_secret, encrypted_derived_key) = crypto.pk_encrypt_string(
                            secret, identitydb.iddb[recipient])
                    else:
                        (encrypted_secret, encrypted_derived_key) = crypto.pk_encrypt_string(
                            secret, cert['cert_bytes'])
                encrypted_secrets[cert['fingerprint']] = {
                    'encrypted_secret': encrypted_secret,
                    'derived_key': encrypted_derived_key,
                    'recipient_hash': cert['subjecthash'],
                }
            try:
                distributor_hash = crypto.get_card_subjecthash()
            except X509CertificateError:
                distributor_hash = identitydb.iddb[distributor]['certs'][0]['subjecthash']
            recipient_entry = {
                'encrypted_secrets': encrypted_secrets,
                'encryption_algorithm': encryption_algorithm,
                'timestamp': time(),
                'distributor': distributor,
                'distributor_hash': distributor_hash,
            }
            message = self._create_signable_string(recipient_entry)
            recipient_entry['signature'] = crypto.pk_sign_string(
                message,
                identitydb.iddb[distributor],
                passphrase, card_slot
            )

            return recipient_entry
        except KeyError as err:
            raise NotARecipientError(
                "Identity '%s' is not on the recipient list for password '%s'" %
                (recipient, self.metadata['name'])) from err

        #######################################################################
    def decrypt_entry(self, identity=None, passphrase=None, card_slot=None):
        """ Decrypt this password entry for a particular identity
        (usually the user) """
        #######################################################################
        try:
            recipient_entry = self.recipients[identity['uid']]
        except KeyError as err:
            raise NotARecipientError(
                "Identity '%s' is not on the recipient list for password '%s'" %
                (identity['uid'], self.metadata['name'])) from err

        try:
            # support old yaml format
            return crypto.pk_decrypt_string(
                recipient_entry['encrypted_secret'],
                recipient_entry['derived_key'],
                identity,
                passphrase,
                card_slot)
        except KeyError:
            try:
                # support rsa
                if 'key_path' in identity.keys():
                    for _, value in recipient_entry['encrypted_secrets'].items():
                        return crypto.pk_decrypt_string(
                            value['encrypted_secret'],
                            value['derived_key'],
                            identity,
                            passphrase
                        )
                else:
                    cert_key = crypto.get_card_fingerprint()
                    return crypto.pk_decrypt_string(
                        recipient_entry['encrypted_secrets'][cert_key]['encrypted_secret'],
                        recipient_entry['encrypted_secrets'][cert_key]['derived_key'],
                        identity,
                        passphrase,
                        card_slot)
            except DecryptionError as err:
                msg = create_error_message(recipient_entry['timestamp'], card_slot)
                raise DecryptionError(
                    "Error decrypting password named '%s'. %s" %
                    (self.metadata['name'], msg)) from err
            except KeyError as err:
                raise DecryptionError(
                    "Error decrypting password named '%s'. Appropriate private key not found" %
                    self.metadata['name']) from err
        except DecryptionError as err:
            msg = create_error_message(recipient_entry['timestamp'], card_slot)
            raise DecryptionError("Error decrypting password named '%s'. %s" %
                                  (self.metadata['name'], msg)) from err

        #######################################################################
    def verify_entry(self, uid=None, iddb=None):
        """ Check to see if all signatures and user certificates are okay for
        the user accessing this password entry """
        #######################################################################
        identitydb = iddb.iddb
        recipient_entry = self.recipients[uid].copy()
        distributor = recipient_entry['distributor']
        iddb.verify_identity(distributor, [])
        signature = recipient_entry.pop('signature')
        message = self._create_signable_string(recipient_entry)
        sig_ok = crypto.pk_verify_signature(
            message, signature, identitydb[distributor])
        return {
            'distributor': distributor,
            'sigOK': sig_ok,
            'certOK': identitydb[distributor]['certs'][0]['verified']
        }

        #######################################################################
    def _create_signable_string(self, recipient_entry):
        """ Helper function to create a string out of the information
        this PasswordEntry contains"""
        #######################################################################
        message = ""
        for key in sorted(recipient_entry.keys()):
            if key == 'timestamp':
                recipient_entry[key] = "{0:12.2f}".format(float(recipient_entry[key]))
            if key not in ['signature', 'encrypted_secrets']:
                if isinstance(recipient_entry[key], bytes):
                    recipient_entry[key] = recipient_entry[key].decode('UTF-8')
                message = message + str(key) + str(recipient_entry[key])
        return message

        #######################################################################
    def todict(self):
        """Returns a dictionary"""
        #######################################################################
        return vars(self)

        #######################################################################
    def validate(self):
        """This function validates a password object"""
        #######################################################################
        # for field in ['field1', 'field2']:
        #  if weird: raise PasswordValidationError(field, value)
        return True

        #######################################################################
    def __repr__(self):
        #######################################################################
        return "%s(%r)" % (self.__class__, self.__dict__)

        #######################################################################
    def __str__(self):
        #######################################################################
        return "%r" % self.__dict__

        ##########################################################################
    def read_password_data(self, filename):
        """ Open a password file, load passwords and read metadata"""
        ##########################################################################
        try:
            with open(filename, 'r') as fname:
                password_data = yaml.safe_load(fname)
                self.metadata = password_data['metadata']
                self.recipients = password_data['recipients']
                if 'escrow' in password_data:
                    self.escrow = password_data['escrow']
            self.validate()
        except (OSError, IOError) as error:
            raise PasswordIOError(
                "Error Opening %s due to %s" %
                (filename, error.strerror)) from error
        except (yaml.scanner.ScannerError, yaml.parser.ParserError) as error:
            raise YamlFormatError(str(error.problem_mark), error.problem) from error

        ############################################################################################
    def write_password_data(self, filename, overwrite=False,
                            export=False,
                            encrypted_export=False,
                            password=None):
        """Write password data to a password file """
        ############################################################################################
        self.validate()
        # check if the file is in the base password directory
        incwd = path.basename(filename) == filename
        # if not ensure path exists
        try:
            if not incwd and not path.isdir(path.dirname(filename)):
                makedirs(path.dirname(filename))
            passdata = {key: value for key, value in self.todict().items() if value}
            open_method = 'a' if export else 'w'
            with open(filename, open_method) as fname:
                if encrypted_export:
                    encrypted = crypto.sk_encrypt_string(
                        yaml.safe_dump(passdata, default_flow_style=False),
                        password)
                    fname.write(encrypted.decode() + "\n")
                else:
                    fname.write(yaml.safe_dump(passdata, default_flow_style=False))
        except (OSError, IOError) as error:
            raise PasswordIOError("Error creating '%s'" % filename) from error

def create_error_message(recipient_timestamp, card_slot):
    card_start = crypto.get_card_startdate()
    card_start = datetime.timestamp(parser.parse(card_start))
    distribute_time = float(recipient_timestamp)
    # Slots are indexed at 0 so when enumerating you add 1
    # There is also an additional information line so add 1 again
    if int(card_slot) + 2 > len(crypto.get_card_info()[0]):
        msg = 'Attempting to use card slot that is not connected'
    elif distribute_time < card_start:
        msg = 'Password distributed before this certificate was created'
    else:
        msg = "Perhaps a bad pin/passphrase?"
    return msg

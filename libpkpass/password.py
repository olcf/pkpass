"""This Module defines what a password contains"""
import time
import os
import yaml
from libpkpass.errors import NotARecipientError, DecryptionError, PasswordIOError
import libpkpass.crypto as crypto


class PasswordEntry(object):
    ##########################################################################
    """ Password entry object.  Contains information about a password and related
        metadata, as well as a list of individually encrypted strings          """
    ##########################################################################

    def __init__(self, **kwargs):

        self.metadata = {'name': None,
                         'description': None,
                         'creator': None,
                         'authorizer': None,
                         'signature': None,
                         'schemaVersion': 'v1'}

        self.metadata.update(kwargs)
        self.recipients = {}

    def add_recipients(
            self,
            secret=None,
            distributor=None,
            recipients=None,
            identitydb=None,
            encryption_algorithm='rsautl',
            passphrase=None, card_slot=None):
        #######################################################################
        """ Add recipients to the recipient list of this password object           """
        #######################################################################
        if recipients is None:
            recipients = []
        for recipient in recipients:
            if encryption_algorithm == 'rsautl':
                (encrypted_secret, encrypted_derived_key) = crypto.pk_encrypt_string(
                    secret, identitydb.iddb[recipient])

            recipient_entry = {'encrypted_secret': encrypted_secret,
                               'derived_key': encrypted_derived_key,
                               'distributor': distributor,
                               'distributor_hash': identitydb.iddb[distributor]['subjecthash'],
                               'recipient_hash': identitydb.iddb[recipient]['subjecthash'],
                               # 'distributor_fingerprint': crypto.get_cert_fingerprint( identitydb.iddb[distributor] ),
                               # 'recipient_fingerprint': crypto.get_cert_fingerprint( identitydb.iddb[recipient] ),
                               'encryption_algorithm': encryption_algorithm,
                               'timestamp': time.time()}

            message = self._create_signable_string(recipient_entry)

            recipient_entry['signature'] = crypto.pk_sign_string(
                message,
                identitydb.iddb[distributor],
                passphrase, card_slot)

            self.recipients[recipient] = recipient_entry

    def decrypt_entry(self, identity=None, passphrase=None, card_slot=None):
        #######################################################################
        """ Decrypt this password entry for a particular identity (usually the user) """
        #######################################################################
        try:
            recipient_entry = self.recipients[identity['uid']]
        except KeyError:
            raise NotARecipientError(
                "Identity '%s' is not on the recipient list for password '%s" %
                (identity['uid'], self.metadata['name']))

        try:
            return crypto.pk_decrypt_string(
                recipient_entry['encrypted_secret'],
                recipient_entry['derived_key'],
                identity,
                passphrase,
                card_slot)
        except DecryptionError:
            raise DecryptionError(
                "Error decrypting password named '%s'.  Perhaps a bad pin/passphrase?" %
                self.metadata['name'])

    def verify_entry(self, uid=None, identitydb=None):
        #######################################################################
        """ Check to see if all signatures and user certificates are okay for the user accessing this password entry """
        #######################################################################
        recipient_entry = self.recipients[uid].copy()
        distributor = recipient_entry['distributor']
        signature = recipient_entry.pop('signature')
        message = self._create_signable_string(recipient_entry)
        sig_ok = crypto.pk_verify_signature(
            message, signature, identitydb[distributor])
        return {'distributor': distributor,
                'sigOK': sig_ok,
                'certOK': identitydb[distributor]['verified']}

    def _create_signable_string(self, recipient_entry):
        #######################################################################
        """ Helper function to create a string out of the information this PasswordEntry contains        """
        #######################################################################
        message = ""
        for key in sorted(recipient_entry.keys()):
            if key != 'signature':
                message = message + str(key) + str(recipient_entry[key])
        return message

    def todict(self):
        """Returns a dictionary"""
        return vars(self)

    def validate(self):
        """This function validates a password object"""
        # for field in ['field1', 'field2']:
        #  if weird: raise PasswordValidationError(field, value)
        return True

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __str__(self):
        return "%r" % self.__dict__

    ##########################################################################

    def read_password_data(self, filename):
        """ Open a password file, load passwords and read metadata               """
    ##########################################################################
        try:
            with open(filename, 'r') as fname:
                password_data = yaml.safe_load(fname)
                self.metadata = password_data['metadata']
                self.recipients = password_data['recipients']
            self.validate()
        except (OSError, IOError) as error:
            raise PasswordIOError(
                "Error Opening %s due to %s" %
                (filename, error.strerror))

    ##########################################################################
    def write_password_data(self, filename, overwrite=False):
        """ Write password data and metadata to the appropriate password file """
    ##########################################################################
        self.validate()
        try:
            if not os.path.isdir(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))
            with open(filename, 'w+') as fname:
                fname.write(yaml.dump(self.todict(), default_flow_style=False))
        except (OSError, IOError):
            raise PasswordIOError("Error creating '%s'" % filename)

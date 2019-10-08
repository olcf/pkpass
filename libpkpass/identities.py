"""This Module handles the identitydb object"""

from __future__ import print_function
import os
import tempfile
import libpkpass.crypto as crypto
from libpkpass.errors import FileOpenError, CliArgumentError

    ##########################################################################
class IdentityDB(object):
    """ User database class.  Contains information about the identities of and
        things pertinent to recipients and their groups and keys.              """
    ##########################################################################

    def __init__(self, **kwargs):
        self.extensions = {'certificate': ['.cert', '.crt'],
                           'key': '.key'}
        self.cabundle = ""
        self.iddb = {}

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __str__(self):
        return "%r" % self.__dict__

    def _load_certs_from_external(self, connection_map):
        if 'base_directory' in connection_map and connection_map['base_directory']:
            temp_dir = connection_map['base_directory']
            del connection_map['base_directory']
        else:
            temp_dir = str(tempfile.gettempdir())

        for key, value in connection_map.items():
            dirname = os.path.join(temp_dir, str(key))
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            if ('cache' not in value or not value['cache']\
                    or not os.listdir(dirname)):
                encoded = key
                connector = "libpkpass.connectors." + encoded.lower()
                connector = __import__(connector, fromlist=[encoded])
                connector = getattr(connector, encoded)
                connector = connector(value)
                # connector.list_certificates() should return a dict
                # the key being the username and the value being
                # a list of certs
                certs = connector.list_certificates()
                for name, certlist in certs.items():
                    with open(os.path.join(dirname, str(name)) +  str(self.extensions['certificate'][0]), 'w') as tmpcert:
                        tmpcert.write("\n".join(certlist))

            self._load_from_directory(dirname, 'certificate')

        #######################################################################
    def _load_from_directory(self, path, filetype):
        """ Helper function to read in (keys|certs) and store them correctly """
        #######################################################################
        try:
            for fname in os.listdir(path):
                if fname.endswith(tuple(self.extensions[filetype])):
                    uid = fname.split('.')[0]
                    filepath = os.path.join(path, fname)
                    try:
                        self.iddb[uid]["%s_path" % filetype] = filepath
                    except KeyError as error:
                        identity = {'uid': fname.split('.')[0],
                                    "%s_path" % filetype: filepath}
                        self.iddb[identity['uid']] = identity
        except OSError as error:
            raise FileOpenError(path, str(error.strerror))

        #######################################################################
    def load_certs_from_directory(self,
                                  certpath,
                                  verify_on_load=False,
                                  connectmap=None):
        """ Read in all x509 certificates from directory and name them as found """
        #######################################################################
        if connectmap:
            self._load_certs_from_external(connectmap)
        if certpath:
            self._load_from_directory(certpath, 'certificate')
        if verify_on_load:
            for key, _ in self.iddb.items():
                self.verify_identity(key)

        #######################################################################
    def verify_identity(self, identity):
        """ Read in all rsa keys from directory and name them as found """
        #######################################################################
        try:
            self.iddb[identity]['cabundle'] = self.cabundle
            self.iddb[identity]['verified'] = crypto.pk_verify_chain(self.iddb[identity])
            self.iddb[identity]['fingerprint'] = crypto.get_cert_fingerprint(
                self.iddb[identity])
            self.iddb[identity]['subject'] = crypto.get_cert_subject(self.iddb[identity])
            self.iddb[identity]['issuer'] = crypto.get_cert_issuer(self.iddb[identity])
            self.iddb[identity]['enddate'] = crypto.get_cert_enddate(self.iddb[identity])
            self.iddb[identity]['issuerhash'] = crypto.get_cert_issuerhash(
                self.iddb[identity])
            self.iddb[identity]['subjecthash'] = crypto.get_cert_subjecthash(
                self.iddb[identity])
        except KeyError:
            raise CliArgumentError(
                "Error: Recipient '%s' is not in the recipient database" % identity)

        #######################################################################
    def load_keys_from_directory(self, path):
        """ Read in all rsa keys from directory and name them as found """
        #######################################################################
        if os.path.isdir(path):
            self._load_from_directory(path, 'key')
        # We used to print a warning on else here, but it seems unnecessary;
        # if a user is using PIVs/Smartcards, this warning could just annoy
        # them needlessly

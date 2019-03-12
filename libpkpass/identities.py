"""This Module handles the identitydb object"""

from __future__ import print_function
import os
import tempfile
import libpkpass.crypto as crypto
from libpkpass.errors import FileOpenError

class IdentityDB(object):
    ##########################################################################
    """ User database class.  Contains information about the identities of and
        things pertinent to recipients and their groups and keys.              """
    ##########################################################################

    def __init__(self, **kwargs):
        self.extensions = {'certificate': ['.cert', '.crt'],
                           'key': '.key'}
        self.iddb = {}

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __str__(self):
        return "%r" % self.__dict__

    def _load_certs_from_external(self, connection_map, nocache):
        temp_dir = str(tempfile.gettempdir())
        for key, value in connection_map.items():
            dirname = os.path.join(temp_dir, str(key))
            if nocache and os.path.exists(dirname):
                encoded = key.encode("ASCII")
                connector = "libpkpass.connectors." + encoded.lower()
                connector = __import__(connector, fromlist=[encoded])
                connector = getattr(connector, encoded)
                connector = connector(value)
                # connector.list_certificates() should return a dict
                # the key being the username and the value being
                # a list of certs
                certs = connector.list_certificates()
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                for name, certlist in certs.items():
                    with open(os.path.join(dirname, str(name)) +  str(self.extensions['certificate'][0]), 'w') as tmpcert:
                        tmpcert.write("\n".join(certlist))

            self._load_from_directory(dirname, 'certificate')

    def _load_from_directory(self, path, filetype):
        #######################################################################
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

    def load_certs_from_directory(self, certpath, cabundle, connectmap=None, noverify=False, nocache=False):
        #######################################################################
        """ Read in all x509 certificates from directory and name them as found """
        #######################################################################
        if connectmap:
            self._load_certs_from_external(connectmap, nocache)
        if certpath:
            self._load_from_directory(certpath, 'certificate')
        for key, _ in self.iddb.items():
            self.iddb[key]['cabundle'] = cabundle
            if not noverify:
                self.iddb[key]['verified'] = crypto.pk_verify_chain(self.iddb[key])
                self.iddb[key]['fingerprint'] = crypto.get_cert_fingerprint(
                    self.iddb[key])
                self.iddb[key]['subject'] = crypto.get_cert_subject(self.iddb[key])
                self.iddb[key]['issuer'] = crypto.get_cert_issuer(self.iddb[key])
                self.iddb[key]['enddate'] = crypto.get_cert_enddate(self.iddb[key])
                self.iddb[key]['issuerhash'] = crypto.get_cert_issuerhash(
                    self.iddb[key])
                self.iddb[key]['subjecthash'] = crypto.get_cert_subjecthash(
                    self.iddb[key])

    def load_keys_from_directory(self, path):
        #######################################################################
        """ Read in all rsa keys from directory and name them as found """
        #######################################################################
        if os.path.isdir(path):
            self._load_from_directory(path, 'key')
        else:
            print("WARNING: PRIVATE KEY DIRECTORY DOES NOT EXIST OR IS NOT POPULATED")

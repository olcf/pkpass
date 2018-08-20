import os
import libpkpass.crypto as crypto
from libpkpass.errors import *


class IdentityDB(object):
    ##########################################################################
    """ User database class.  Contains information about the identities of and
        things pertinent to recipients and their groups and keys.              """
    ##########################################################################

    def __init__(self, **kwargs):
        self.extensions = {'certificate': '.cert',
                           'key': '.key'}
        self.iddb = {}

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __str__(self):
        return "%r" % self.__dict__

    def _load_from_directory(self, path, filetype):
        #######################################################################
        """ Helper function to read in (keys|certs) and store them correctly """
        #######################################################################
        try:
            for f in os.listdir(path):
                if f.endswith(self.extensions[filetype]):
                    uid = f.split('.')[0]
                    filepath = os.path.join(path, f)
                    try:
                        self.iddb[uid]["%s_path" % filetype] = filepath
                    except KeyError as e:
                        identity = {'uid': f.split('.')[0],
                                    "%s_path" % filetype: filepath}
                        self.iddb[identity['uid']] = identity
        except OSError as e:
            raise FileOpenError(path, str(e.strerror))

    def load_certs_from_directory(self, certpath, cabundle):
        #######################################################################
        """ Read in all x509 certificates from directory and name them as found """
        #######################################################################
        self._load_from_directory(certpath, 'certificate')
        for key in self.iddb.keys():
            self.iddb[key]['cabundle'] = cabundle
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
        self._load_from_directory(path, 'key')

"""This Module handles the identitydb object"""
from os import path, listdir
from datetime import datetime
from pem import parse_file
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm
from libpkpass.crypto import pk_verify_chain, get_cert_fingerprint, get_cert_subject,\
    get_cert_issuer, get_cert_enddate, get_cert_issuerhash, get_cert_subjecthash
from libpkpass.errors import FileOpenError, CliArgumentError
from libpkpass.models.recipient import Recipient
from libpkpass.models.cert import Cert
from libpkpass.util import create_or_update


    ##########################################################################
class IdentityDB():
    """ User database class.  Contains information about the identities of and
        things pertinent to recipients and their groups and keys.              """
    ##########################################################################

        #######################################################################
    def __init__(self):
        #######################################################################
        self.extensions = {'certificate': ['.cert', '.crt'],
                           'key': '.key'}
        self.cabundle = ""
        self.args = {}

        #######################################################################
    def __repr__(self):
        #######################################################################
        return f"{self.__class__}({self.__dict__})"

        #######################################################################
    def __str__(self):
        #######################################################################
        return f"{self.__dict__}"

        #######################################################################
    def _load_certs_from_external(self, connection_map):
        """Load certificates from external via use of plugin"""
        #######################################################################
        if 'base_directory' in connection_map and connection_map['base_directory']:
            del connection_map['base_directory']
        for key, value in connection_map.items():
            connector = getattr(__import__(key.lower(), fromlist=[key]), key)(value)
            certs = connector.list_certificates()
            print("Loading certs into database")
            for name, certlist in tqdm(certs.items()):
                self.load_db(name, certlist)

        #######################################################################
    def _load_from_directory(self, fpath, filetype):
        """ Helper function to read in (keys|certs) and store them correctly """
        #######################################################################
        try:
            print("Loading certs into database")
            for fname in tqdm(listdir(fpath)):
                if fname.endswith(tuple(self.extensions[filetype])):
                    uid = fname.split('.')[0]
                    filepath = path.join(fpath, fname)
                    if filetype == 'certificate':
                        self.load_db(uid, certlist=[x.as_text() for x in parse_file(filepath)])
                    elif filetype == 'key':
                        session = sessionmaker(bind=self.args['db']['engine'])()
                        create_or_update(session,
                                         Recipient,
                                         unique_identifiers=['name'],
                                         **{
                                             'name': uid,
                                             'key': filepath,
                                         },
                                         )
                        session.commit()
        except OSError as error:
            raise FileOpenError(fpath, str(error.strerror)) from error

        #######################################################################
    def load_certs_from_directory(self,
                                  certpath,
                                  connectmap=None,
                                  nocache=False):
        """ Read in all x509 certificates from directory and name them as found """
        #######################################################################
        session = sessionmaker(bind=self.args['db']['engine'])()
        if not session.query(Recipient).first() or nocache:
            if certpath:
                self._load_from_directory(certpath, 'certificate')
            if connectmap:
                self._load_certs_from_external(connectmap)

        #######################################################################
    def load_db(self, identity, certlist=None):
        """ Read in all rsa keys from directory and name them as found
        """
        #######################################################################
        try:
            session = sessionmaker(bind=self.args['db']['engine'])()
            recipient = create_or_update(session, Recipient, dont_update=['key'], **{'name': identity})
            for cert in certlist:
                cert = cert.encode()
                cert_dict = {}
                cert_dict['cert_bytes'] = cert
                cert_dict['verified'] = pk_verify_chain(cert, self.cabundle)
                cert_dict['fingerprint'] = get_cert_fingerprint(cert)
                cert_dict['subject'] = get_cert_subject(cert)
                cert_dict['issuer'] = get_cert_issuer(cert)
                cert_dict['enddate'] = datetime.strptime(get_cert_enddate(cert), '%b %d %H:%M:%S %Y %Z')
                cert_dict['issuerhash'] = get_cert_issuerhash(cert)
                cert_dict['subjecthash'] = get_cert_subjecthash(cert)
                cert = create_or_update(
                    session,
                    Cert,
                    unique_identifiers=['fingerprint'],
                    **cert_dict
                )
                if cert not in recipient.certs:
                    recipient.certs.append(cert)
            session.commit()
        except KeyError as err:
            raise CliArgumentError(
                f"Error: Recipient '{identity}' is not in the recipient database"
            ) from err

    def verify_identity(self, identity):
        session = sessionmaker(bind=self.args['db']['engine'])()
        recipient = session.query(Recipient).filter(Recipient.name == identity).first()
        if not recipient:
            return False
        for cert in session.query(Cert).filter(
                Cert.recipients.contains(recipient)
        ).all():
            if not cert.verified:
                return False
        return True

        #######################################################################
    def load_keys_from_directory(self, fpath):
        """ Read in all rsa keys from directory and name them as found """
        #######################################################################
        if path.isdir(fpath):
            self._load_from_directory(fpath, 'key')
        # We used to print a warning on else here, but it seems unnecessary;
        # if a user is using PIVs/Smartcards, this warning could just annoy
        # them needlessly

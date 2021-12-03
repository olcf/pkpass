#!/usr/bin/env python3
"""This Module tests crypto functionality"""
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from libpkpass.crypto import pk_encrypt_string, pk_decrypt_string, \
    pk_sign_string, pk_verify_signature, get_cert_fingerprint
from libpkpass.identities import IdentityDB
from libpkpass.models.recipient import Recipient
from libpkpass.models.cert import Cert

class TestBasicFunction(unittest.TestCase):
    """This class tests the crypto class"""
    def setUp(self):
        self.plaintext = "PLAINTEXT"

        self.certdir = 'test/pki/intermediate/certs'
        self.keydir = 'test/pki/intermediate/private'
        self.cabundle = 'test/pki/intermediate/certs/ca-bundle'

        self.identities = IdentityDB()
        db_path = 'test/pki/intermediate/certs/rd.db'
        self.identities.args = {
            'db': {
                'uri': f"sqlite+pysqlite:///{db_path}",
                'engine': create_engine(f"sqlite+pysqlite:///{db_path}")
            }
        }
        self.session = sessionmaker(bind=self.identities.args['db']['engine'])()
        self.identities.load_certs_from_directory(self.certdir, self.cabundle)
        self.identities.load_keys_from_directory(self.keydir)

    # Encrypt strings for all test identities and make sure they are different
    def test_encrypt_string(self):
        """Test encrypting a string"""
        results = []
        for identity in self.session.query(Recipient).all():
            cert = self.session.query(Cert).filter(
                Cert.recipients.contains(identity)
            ).first()
            results.append(
                pk_encrypt_string(
                    self.plaintext, cert.cert_bytes
                )
            )
        self.assertTrue(results[0] != results[1])

    # Encrypt/Decrypt strings for all test identities and make sure we get back what we put in
        for identity in self.session.query(Recipient).all():
            cert = self.session.query(Cert).filter(
                Cert.recipients.contains(identity)
            ).first()
            (ciphertext, derived_key) = pk_encrypt_string(
                self.plaintext, cert.cert_bytes)
            plaintext = pk_decrypt_string(
                ciphertext, derived_key, dict(identity), None)
            self.assertEqual(self.plaintext, plaintext)

    def test_verify_string(self):
        """verify string is correct"""
        results = []
        for identity in self.session.query(Recipient).all():
            results.append(pk_sign_string(
                self.plaintext, dict(identity), None))
        self.assertTrue(results[0] != results[1])

        for identity in self.session.query(Recipient).all():
            signature = pk_sign_string(self.plaintext, dict(identity), None)
            cert = self.session.query(Cert).filter(
                Cert.recipients.contains(identity)
            ).first()
            self.assertTrue(pk_verify_signature(
                self.plaintext, signature, [cert]))

    def test_cert_fingerprint(self):
        """Verify fingerprint is correct"""
        for identity in self.session.query(Recipient).all():
            cert = self.session.query(Cert).filter(
                Cert.recipients.contains(identity)
            ).first()
            fingerprint = get_cert_fingerprint(cert.cert_bytes)
            self.assertTrue(len(fingerprint.split(':')) == 20)


if __name__ == '__main__':
    unittest.main()

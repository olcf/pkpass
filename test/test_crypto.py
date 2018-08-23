#!/usr/bin/env python
"""This Module tests crypto functionality"""

import unittest
import libpkpass.crypto as crypto
from libpkpass.identities import IdentityDB


class TestBasicFunction(unittest.TestCase):
    """This class tests the crypto class"""
    def setUp(self):
        self.plaintext = "PLAINTEXT"

        self.certdir = 'test/pki/intermediate/certs'
        self.keydir = 'test/pki/intermediate/private'
        self.cabundle = 'test/pki/intermediate/certs/ca-bundle'

        self.identities = IdentityDB()
        self.identities.load_certs_from_directory(self.certdir, self.cabundle)
        self.identities.load_keys_from_directory(self.keydir)

    # Encrypt strings for all test identities and make sure they are different
    def test_encrypt_string(self):
        """Test encrypting a string"""
        results = []
        for _, identity in self.identities.iddb.iteritems():
            results.append(crypto.pk_encrypt_string(self.plaintext, identity))
        self.assertTrue(results[0] != results[1])

    # Encrypt/Decrypt strings for all test identities and make sure we get back what we put in
        for _, identity in self.identities.iddb.iteritems():
            (ciphertext, derived_key) = crypto.pk_encrypt_string(
                self.plaintext, identity)
            plaintext = crypto.pk_decrypt_string(
                ciphertext, derived_key, identity, None)
            self.assertTrue(self.plaintext == plaintext)

    def test_verify_string(self):
        """verify string is correct"""
        results = []
        for _, identity in self.identities.iddb.iteritems():
            results.append(crypto.pk_sign_string(
                self.plaintext, identity, None))
        self.assertTrue(results[0] != results[1])

        for _, identity in self.identities.iddb.iteritems():
            signature = crypto.pk_sign_string(self.plaintext, identity, None)
            self.assertTrue(crypto.pk_verify_signature(
                self.plaintext, signature, identity))

    def test_cert_fingerprint(self):
        """Verify fingerprint is correct"""
        for _, identity in self.identities.iddb.iteritems():
            fingerprint = crypto.get_cert_fingerprint(identity)
            self.assertTrue(len(fingerprint.split(':')) == 20)


if __name__ == '__main__':
    unittest.main()

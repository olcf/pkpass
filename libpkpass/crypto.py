#!/usr/bin/env python
"""This Module handles the crypto functions i.e. encryption and decryption"""

import base64
import tempfile
import os
import hashlib
from subprocess import Popen, PIPE, STDOUT
from cryptography.fernet import Fernet
from libpkpass.errors import EncryptionError, DecryptionError, SignatureCreationError, \
        SignatureVerificationError, TrustChainVerificationError, X509CertificateError


##############################################################################
def pk_encrypt_string(plaintext_string, identity):
    """ Encrypt and return a base 64 encoded string for the provided identity"""
##############################################################################

    plaintext_derived_key = Fernet.generate_key()

    command = "openssl rsautl -inkey -certin -encrypt -pkcs".split()
    command.insert(3, identity['certificate_path'])
    proc = Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    stdout, _ = proc.communicate(input=plaintext_derived_key)

    if proc.returncode != 0:
        raise EncryptionError("Error encrypting derived key: %s" % stdout)
    ciphertext_derived_key = stdout

    fern = Fernet(plaintext_derived_key)
    encrypted_string = fern.encrypt(plaintext_string)

    return (encrypted_string, base64.urlsafe_b64encode(ciphertext_derived_key))


##############################################################################
def pk_decrypt_string(ciphertext_string, ciphertext_derived_key, identity, passphrase, card_slot=None):
    """ Decrypt a base64 encoded string for the provided identity"""
##############################################################################

    if 'key_path' in identity:
        command = "openssl rsautl -inkey -decrypt -pkcs".split()
        command.insert(3, identity['key_path'])
        proc = Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        stdout, _ = proc.communicate(
            input=base64.urlsafe_b64decode(ciphertext_derived_key))
        plaintext_derived_key = stdout
    else:
        # We've got to use pkcs15-crypt for PIV cards, and it only supports pin on
        # command line (insecure) or via stdin.  So, we have to put ciphertext into
        # a file for pkcs15-crypt to read.  YUCK!
        with tempfile.NamedTemporaryFile(delete=False) as fname:
            fname.write(base64.urlsafe_b64decode(ciphertext_derived_key))
        command = "pkcs15-crypt --decipher --raw --pkcs --input --pin -".split()
        command.insert(5, fname.name)
        index = 1
        if card_slot is not None:
            command.insert(6, "--reader")
            command.insert(7, str(card_slot))
            index = 0
        proc = Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        stdout, _ = proc.communicate(input=passphrase)
        os.unlink(fname.name)
        try:
            plaintext_derived_key = stdout.splitlines()[index]
        except IndexError:
            raise DecryptionError(stdout)

    if proc.returncode != 0:
        raise DecryptionError(stdout)

    fern = Fernet(plaintext_derived_key)
    plaintext_string = fern.decrypt(ciphertext_string)

    return plaintext_string


##############################################################################
def pk_sign_string(string, identity, passphrase, card_slot=None):
    """ Compute the hash of string and create a digital signature """
##############################################################################
    stringhash = hashlib.sha256(string).hexdigest()
    if 'key_path' in identity:
        command = 'openssl rsautl -sign -inkey'.split()
        command.insert(4, identity['key_path'])
        proc = Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        stdout, _ = proc.communicate(input=stringhash)
        signature = base64.urlsafe_b64encode(stdout)
    else:
        # We've got to use pkcs15-crypt for PIV cards, and it only supports pin on
        # command line (insecure) or via stdin.  So, we have to put signature text
        # into a file for pkcs15-crypt to read.  YUCK!
        with tempfile.NamedTemporaryFile(delete=False) as fname:
            fname.write(stringhash)
        out = tempfile.NamedTemporaryFile(delete=False)
        command = 'pkcs15-crypt --sign -i -o --pkcs1 --raw --pin -'.split()
        command.insert(3, fname.name)
        command.insert(5, out.name)
        if card_slot is not None:
            command.insert(7, "--reader")
            command.insert(8, str(card_slot))
        proc = Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        stdout, _ = proc.communicate(input=passphrase)
        out.close()

        with open(out.name, 'r') as sigfile:
            signature = base64.urlsafe_b64encode(sigfile.read())

        os.unlink(fname.name)
        os.unlink(out.name)

    if proc.returncode != 0:
        raise SignatureCreationError(stdout)

    return signature


##############################################################################
def pk_verify_signature(string, signature, identity):
    """ Compute the hash of string and verify the digital signature """
##############################################################################
    stringhash = hashlib.sha256(string).hexdigest()
    command = 'openssl rsautl -inkey -certin -verify'.split()
    command.insert(3, identity['certificate_path'])
    proc = Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    stdout, _ = proc.communicate(input=base64.urlsafe_b64decode(signature))

    if proc.returncode != 0:
        raise SignatureVerificationError(stdout)

    return stdout == stringhash


##############################################################################
def pk_verify_chain(identity):
    """ Verify the publickey trust chain against a CA Bundle and return True if valid"""
##############################################################################
    command = 'openssl verify -CAfile'.split()
    command.insert(3, identity['cabundle'])
    command.insert(4, identity['certificate_path'])
    proc = Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    stdout, _ = proc.communicate()

    if proc.returncode != 0:
        raise TrustChainVerificationError(stdout)

    return stdout.rstrip() == "%s: OK" % identity['certificate_path']


##############################################################################
def get_cert_fingerprint(identity):
    """ Return the modulus of the x509 certificate of the identity """
##############################################################################
    # SHA1 Fingerprint=F9:9D:71:54:55:BE:99:24:6A:5E:E0:BB:48:F9:63:AE:A2:05:54:98
    return get_cert_element(identity, 'fingerprint').split('=')[1]


##############################################################################
def get_cert_subject(identity):
    """ Return the subject DN of the x509 certificate of the identity """
##############################################################################
    # subject= /C=US/O=Entrust/OU=Certification Authorities/OU=Entrust Managed Services SSP CA
    return ' '.join(get_cert_element(identity, 'subject').split(' ')[1:])


##############################################################################
def get_cert_issuer(identity):
    """ Return the issuer DN of the x509 certificate of the identity """
##############################################################################
    # issuer= /C=US/O=Entrust/OU=Certification Authorities/OU=Entrust Managed Services SSP CA
    return ' '.join(get_cert_element(identity, 'issuer').split(' ')[1:])


##############################################################################
def get_cert_enddate(identity):
    """ Return the issuer DN of the x509 certificate of the identity """
##############################################################################
    return get_cert_element(identity, 'enddate').split('=')[1]


##############################################################################
def get_cert_issuerhash(identity):
    """ Return the issuer DN of the x509 certificate of the identity """
##############################################################################
    return get_cert_element(identity, 'issuer_hash')


##############################################################################
def get_cert_subjecthash(identity):
    """ Return the issuer DN of the x509 certificate of the identity """
##############################################################################
    return get_cert_element(identity, 'subject_hash')


##############################################################################
def get_cert_element(identity, element):
    """ Return an arbitrary element of an x509 certificate """
##############################################################################

    command = "openssl x509 -in -noout".split()
    command.insert(3, identity['certificate_path'])
    command.append("-%s" % element)
    proc = Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    stdout, _ = proc.communicate()

    if proc.returncode != 0:
        raise X509CertificateError(stdout)

    try:
        return stdout.rstrip()
    except IndexError:
        raise X509CertificateError(stdout)


##############################################################################
def sk_encrypt_string(plaintext_string, key):
    """ Symmetrically Encrypt and return a base 64 encoded string using the provided secret"""
##############################################################################

    fern = Fernet(key)
    encrypted_string = fern.encrypt(plaintext_string)
    return base64.urlsafe_b64encode(encrypted_string)


##############################################################################
def sk_decrypt_string(ciphertext_string, key):
    """ Symmetrically Decrypt a base64 encoded string using the provided key"""
##############################################################################

    fern = Fernet(key)
    plaintext_string = fern.decrypt(base64.urlsafe_b64decode(ciphertext_string))
    return plaintext_string

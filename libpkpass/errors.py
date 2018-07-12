#!/usr/bin/python


class PKPassError(Exception):
    """Base class for pkpass exceptions."""

    def __init__(self, arg):
        self.msg = arg


class DecryptionError(PKPassError):
    pass


class EncryptionError(PKPassError):
    pass


class SignatureCreationError(PKPassError):
    pass


class SignatureVerificationError(PKPassError):
    pass


class TrustChainVerificationError(PKPassError):
    pass


class NotARecipientError(PKPassError):
    pass


class RSAKeyError(PKPassError):
    pass


class X509CertificateError(PKPassError):
    pass


class PasswordMismatchError(PKPassError):
    def __init__(self):
        self.msg = "Passwords do not match"


class PasswordValidationError(PKPassError):
    def __init__(self, field, value):
        self.msg = "Error validating password field: %s with value %s" % (
            field, value)


class PasswordIOError(PKPassError):
    pass


class CliArgumentError(PKPassError):
    pass


class FileOpenError(PKPassError):
    def __init__(self, value, reason):
        self.msg = "File %s found in config, could not be opened due to %s" % (
            value, reason)


class NullRecipientError(PKPassError):
    def __init__(self):
        self.msg = "There is a blank Recipient in the list, please check for trailing commas"

class NoRCFile(PKPassError):
    def __init__(self):
        self.msg = "No .pkpassrc file found, consider running ./setup.sh"

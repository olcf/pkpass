#!/usr/bin/python
"""This Module is the base module for custom errors to allow for reduced tracebacks and
more actionable items on the user's side"""

class PKPassError(Exception):
    """Base class for pkpass exceptions."""

    def __init__(self, arg):
        self.msg = arg

class BlankPasswordError(PKPassError):
    def __init__(self):
        self.msg = "User Provided password is blank or only spaces"

class CliArgumentError(PKPassError):
    pass

class DecryptionError(PKPassError):
    pass

class EncryptionError(PKPassError):
    pass

class EscrowError(PKPassError):
    def __init__(self, field, constant, value):
        self.msg = "%s, must be greater than %s, current value: %s" % (
            field, constant, value)

class FileOpenError(PKPassError):
    def __init__(self, value, reason):
        self.msg = "File %s found in config, could not be opened due to %s" % (
            value, reason)

class GroupDefinitionError(PKPassError):
    def __init__(self, value):
        self.msg = "Group %s is not defined in the config" % (value)

class JsonArgumentError(PKPassError):
    def __init__(self, value, reason):
        self.msg = "Parse error for '%s' because '%s'" %  (value, reason)

class LegacyImportFormatError(PKPassError):
    def __init__(self):
        self.msg = "Passwords in import file not in key:value notation"

class NotARecipientError(PKPassError):
    pass

class NotThePasswordOwnerError(PKPassError):
    def __init__(self, identity, owner, pwname):
        self.msg = "User '%s' is not the owner of password '%s', not overwriting;\n\t\
please use another password name or ask the owner (%s) to distribute to you" % (identity, pwname, owner)

class NullRecipientError(PKPassError):
    def __init__(self):
        self.msg = "There is a blank Recipient in the list, please check for trailing commas"

class PasswordIOError(PKPassError):
    pass

class PasswordMismatchError(PKPassError):
    def __init__(self):
        self.msg = "Passwords do not match"

class PasswordValidationError(PKPassError):
    def __init__(self, field, value):
        self.msg = "Error validating password field: %s with value %s" % (
            field, value)

class RulesMapError(PKPassError):
    def __init__(self, reason):
        self.msg = reason

class RSAKeyError(PKPassError):
    pass

class SignatureCreationError(PKPassError):
    pass

class SignatureVerificationError(PKPassError):
    pass

class TrustChainVerificationError(PKPassError):
    pass

class X509CertificateError(PKPassError):
    pass

class YamlFormatError(PKPassError):
    def __init__(self, value, reason):
        self.msg = "Error%s due to: %s" % (value, reason)

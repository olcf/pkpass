#!/usr/bin/env python3
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

class ConfigParseError(PKPassError):
    pass

class DecryptionError(PKPassError):
    pass

class EncryptionError(PKPassError):
    pass

class EscrowError(PKPassError):
    def __init__(self, field, constant, value):
        self.msg = f"{field}, must be greater than {constant}, current value: {value}"

class FileOpenError(PKPassError):
    def __init__(self, value, reason):
        self.msg = f"File {value} found in config, could not be opened due to {reason}"

class GroupDefinitionError(PKPassError):
    def __init__(self, value):
        self.msg = f"Group {value} is not defined in the config"

class JsonArgumentError(PKPassError):
    def __init__(self, value, reason):
        self.msg = f"Parse error for '{value}' because '{reason}'"

class LegacyImportFormatError(PKPassError):
    def __init__(self):
        self.msg = "Passwords in import file not in key:value notation"

class NotARecipientError(PKPassError):
    pass

class NotThePasswordOwnerError(PKPassError):
    def __init__(self, identity, owner, pwname):
        self.msg = f"User '{identity}' is not the owner of password '{pwname}', not overwriting;\n\t\
please use another password name or ask the owner ({owner}) to distribute to you"

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
        self.msg = f"Error validating password field: {field} with value {value}"

class RulesMapError(PKPassError):
    def __init__(self, reason):
        self.msg = reason

class RSAKeyError(PKPassError):
    pass

class SignatureCreationError(PKPassError):
    pass

class TrustChainVerificationError(PKPassError):
    pass

class X509CertificateError(PKPassError):
    pass

class YamlFormatError(PKPassError):
    def __init__(self, value, reason):
        self.msg = f"Error {value} due to: {reason}"

#!/usr/bin/env python3
"""This Module handles the crypto functions i.e. encryption and decryption"""
from base64 import urlsafe_b64decode, urlsafe_b64encode
from tempfile import NamedTemporaryFile
from os import unlink, environ
from hashlib import sha256
from shutil import get_terminal_size
from subprocess import Popen, PIPE, STDOUT, DEVNULL
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from libpkpass.util import color_prepare
from libpkpass.errors import (
    EncryptionError,
    DecryptionError,
    SignatureCreationError,
    X509CertificateError,
    BadBackendError,
    PKPassError,
)


def handle_python_strings(string):
    ####################################################################
    """handles py2/3 incompatiblities"""
    ####################################################################
    return string if isinstance(string, bytes) else string.encode("UTF-8")


def pk_encrypt_string(plaintext_string, certificate):
    ####################################################################
    """Encrypt and return a base 64 encoded string for the provided identity"""
    ####################################################################
    plaintext_derived_key = Fernet.generate_key()
    with NamedTemporaryFile(delete=False) as fname:
        fname.write(certificate)
        cert_file_path = fname.name
    command = [
        "openssl",
        "pkeyutl",
        "-encrypt",
        "-certin",
        "-inkey",
        cert_file_path,
        "-pkeyopt",
        "rsa_padding_mode:pkcs1"
    ]
    with Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT) as proc:
        stdout, _ = proc.communicate(input=plaintext_derived_key)
        if isinstance(certificate, bytes):
            unlink(fname.name)

        if proc.returncode != 0:
            raise EncryptionError(f"Error encrypting derived key: {stdout}")
        ciphertext_derived_key = stdout

    encrypted_string = Fernet(plaintext_derived_key).encrypt(
        handle_python_strings(plaintext_string)
    )
    return (
        encrypted_string,
        urlsafe_b64encode(handle_python_strings(ciphertext_derived_key)),
    )


def get_card_info(SCBackend="opensc"):
    if SCBackend == "opensc":
        command = ["pkcs11-tool", "-L"]
        with Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT) as proc:
            stdout, _ = proc.communicate()
            return (handle_python_strings(stdout).split(b"Slot"), stdout)
    elif SCBackend == "yubi":
        command = ["yubico-piv-tool", "-a", "list-readers"]
        with Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT) as proc:
            stdout, _ = proc.communicate()
            return (handle_python_strings(stdout).splitlines(), stdout)
    raise BadBackendError(SCBackend)


def print_card_info(card_slot, identity, verbosity, color, theme_map, SCBackend):
    ####################################################################
    """Inform the user what card is selected"""
    ####################################################################
    if "key" not in identity or not identity["key"]:
        out_list, stdout = get_card_info(SCBackend)
        if verbosity > 1:
            yield print_all_slots(stdout, color, theme_map)
        if SCBackend == "opensc":
            for out in out_list[1:]:
                stripped = out.decode("UTF-8").strip()
                if int(stripped[0]) == int(card_slot):
                    verbosity = verbosity + 1 if verbosity < 2 else 2
                    stripped = "Using Slot" + ("\n").join(stripped.split("\n")[:verbosity])
                    yield f"{color_prepare(stripped, 'info', color, theme_map)}"
        elif SCBackend == "yubi":
            for out in out_list:
                stripped = out.decode("UTF-8").strip()
                if "Yubico" not in stripped:
                    # exit(1)
                    raise PKPassError("Unsupported SC type for backend yubi.\nYubico not in:\n" + stripped)
                if int(stripped.split('CCID')[1] or 0) == int(card_slot):
                    verbosity = verbosity + 1 if verbosity < 2 else 2
                    stripped = "Using Slot" + ("\n").join(stripped.split("\n")[:verbosity])
                    yield f"{color_prepare(stripped, 'info', color, theme_map)}"
        else:
            raise BadBackendError(SCBackend)


def print_all_slots(slot_info, color, theme_map):
    ####################################################################
    """Print all slots and cards available"""
    ####################################################################
    columns = int(get_terminal_size().columns) // 4
    return (
        f'{color_prepare("#" * columns, "debug", color, theme_map)}\n'
        f'{handle_python_strings(slot_info).decode("UTF-8").strip()}\n'
        f'{color_prepare("#" * columns, "debug", color, theme_map)}\n'
    )


def pk_decrypt_string(
    ciphertext_string, ciphertext_derived_key, identity, passphrase, SCBackend="opensc", card_slot=None, PKCS11_module_path="/usr/local/lib/libykcs11.dylib"
):
    ####################################################################
    """Decrypt a base64 encoded string for the provided identity"""
    ####################################################################
    ciphertext_derived_key = handle_python_strings(ciphertext_derived_key)
    if "key" in identity and identity["key"]:
        command = ["openssl", "pkeyutl", "-decrypt", "-inkey", identity["key"], "-pkeyopt", "rsa_padding_mode:pkcs1"]
        with Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT) as proc:
            stdout, _ = proc.communicate(
                input=urlsafe_b64decode(ciphertext_derived_key)
            )
            returncode = proc.returncode
        plaintext_derived_key = stdout
    else:
        if SCBackend == "opensc":
            # We've got to use pkcs15-crypt for PIV cards, and it only supports pin on
            # command line (insecure) or via stdin.  So, we have to put ciphertext into
            # a file for pkcs15-crypt to read.  YUCK!
            with NamedTemporaryFile(delete=False) as fname:
                fname.write(urlsafe_b64decode(ciphertext_derived_key))
            command = [
                "pkcs15-crypt",
                "--decipher",
                "--raw",
                "--pkcs",
                "--input",
                fname.name,
            ]
            if card_slot is not None:
                command.extend(["--reader", str(card_slot)])
            command.extend(["--pin", "-"])
            with Popen(command, stdout=PIPE, stdin=PIPE, stderr=DEVNULL) as proc:
                stdout, _ = proc.communicate(input=passphrase.encode("UTF-8"))
                unlink(fname.name)
                try:
                    plaintext_derived_key = stdout
                except IndexError as err:
                    raise DecryptionError(stdout) from err
                returncode = proc.returncode
        elif SCBackend == "yubi":
            # todo: this can be improved to not use temp files
            # https://developers.yubico.com/yubico-piv-tool/YKCS11/Supported_applications/openssl_engine.html
            with NamedTemporaryFile(delete=False) as fname:
                fname.write(urlsafe_b64decode(ciphertext_derived_key))
            command = [
                "openssl",
                "pkeyutl",
                "-decrypt",
                "-engine", "pkcs11",
                "-keyform", "engine",
                "-inkey", "pkcs11:type=private;pin-value=" + passphrase + ";serial=" + get_card_serial(card_slot),
                "-pkeyopt", "rsa_padding_mode:pkcs1",
                "-in", fname.name
            ]
            with Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT, env=dict(environ, PKCS11_MODULE_PATH=PKCS11_module_path)) as proc:
                stdout, _ = proc.communicate(
                    input=urlsafe_b64decode(ciphertext_derived_key)
                )
                try:
                    plaintext_derived_key = str(stdout).split("\\n")[1]
                except IndexError as err:
                    raise DecryptionError(stdout) from err
                returncode = proc.returncode
        else:
            raise BadBackendError(SCBackend)

    if returncode != 0:
        raise DecryptionError(stdout)

    return (
        Fernet(plaintext_derived_key)
        .decrypt(handle_python_strings(ciphertext_string))
        .decode("UTF-8")
    )


def pk_sign_string(string, identity, passphrase, SCBackend="opensc", card_slot=None, PKCS11_module_path="/usr/local/lib/libykcs11.dylib"):
    ####################################################################
    """Compute the hash of string and create a digital signature"""
    ####################################################################
    stringhash = sha256(string.encode("UTF-8")).hexdigest()
    if "key" in identity and identity["key"]:
        command = ["openssl", "pkeyutl", "-sign", "-inkey", identity["key"]]
        with Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT) as proc:
            stdout, _ = proc.communicate(input=stringhash.encode("UTF-8"))
            signature = urlsafe_b64encode(handle_python_strings(stdout))
            returncode = proc.returncode
    else:
        if SCBackend == "opensc":
            # We've got to use pkcs15-crypt for PIV cards, and it only supports pin on
            # command line (insecure) or via stdin.  So, we have to put signature text
            # into a file for pkcs15-crypt to read.  YUCK!
            with NamedTemporaryFile(delete=False) as fname:
                fname.write(stringhash.encode("UTF-8"))
            with NamedTemporaryFile(delete=False) as out:
                command = [
                    "pkcs15-crypt",
                    "--sign",
                    "-i",
                    fname.name,
                    "-o",
                    out.name,
                    "--pkcs1",
                    "--raw",
                ]
                if card_slot is not None:
                    command.extend(["--reader", str(card_slot)])
                command.extend(["--pin", "-"])
                with Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT) as proc:
                    stdout, _ = proc.communicate(input=passphrase.encode("UTF-8"))
                returncode = proc.returncode

            with open(out.name, "rb") as sigfile:
                signature = urlsafe_b64encode(handle_python_strings(sigfile.read()))
        elif SCBackend == "yubi":
            # todo: this can be improved to not use temp files
            # https://developers.yubico.com/yubico-piv-tool/YKCS11/Supported_applications/openssl_engine.html
            with NamedTemporaryFile(delete=False) as fname:
                fname.write(stringhash.encode("UTF-8"))
            with NamedTemporaryFile(delete=False) as out:
                command = [
                    "openssl",
                    "pkeyutl",
                    "-sign",
                    "-engine", "pkcs11",
                    "-keyform", "engine",
                    "-inkey", "pkcs11:type=private;pin-value=" + passphrase + ";serial=" + get_card_serial(card_slot),
                    "-pkeyopt", "rsa_padding_mode:pkcs1",
                    "-in", fname.name,
                    "-out", out.name
                ]
                with Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT, env=dict(environ, PKCS11_MODULE_PATH=PKCS11_module_path)) as proc:
                    stdout, _ = proc.communicate(
                        input=stringhash.encode("UTF-8")
                    )
                returncode = proc.returncode
            with open(out.name, "rb") as sigfile:
                signature = urlsafe_b64encode(handle_python_strings(sigfile.read()))
        else:
            raise BadBackendError(SCBackend)

        unlink(fname.name)
        unlink(out.name)

    if returncode != 0:
        raise SignatureCreationError(stdout)

    return signature


def pk_verify_signature(string, signature, certs):
    ####################################################################
    """Compute the hash of string and verify the digital signature"""
    ####################################################################
    stringhash = sha256(string.encode("UTF-8")).hexdigest()
    for cert in certs:
        with NamedTemporaryFile(delete=False) as fname:
            fname.write(cert.cert_bytes)
        command = ["openssl", "pkeyutl", "-verifyrecover", "-certin", "-inkey", fname.name]
        with Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT) as proc:
            stdout, _ = proc.communicate(
                input=urlsafe_b64decode(handle_python_strings(signature))
            )
            unlink(fname.name)
            if stdout.decode("UTF-8") == stringhash:
                return True

    return stdout.decode("UTF-8") == stringhash


def pk_verify_chain(certificate, cabundle):
    ####################################################################
    """Verify the publickey trust chain against a CA Bundle and return True if valid"""
    ####################################################################
    command = ["openssl", "verify", "-CAfile", cabundle]
    with Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT) as proc:
        stdout, _ = proc.communicate(input=certificate)

    return stdout.decode("UTF-8").rstrip() == "stdin: OK"


def get_cert_fingerprint(cert):
    ####################################################################
    """Return the modulus of the x509 certificate of the identity"""
    ####################################################################
    # SHA1 Fingerprint=F9:9D:71:54:55:BE:99:24:6A:5E:E0:BB:48:F9:63:AE:A2:05:54:98
    return get_cert_element(cert, "fingerprint").split("=")[1]


def get_cert_subject(cert):
    ####################################################################
    """Return the subject DN of the x509 certificate of the identity"""
    ####################################################################
    # subject= /C=US/O=Entrust/OU=Certification Authorities/OU=Entrust Managed Services SSP CA
    return " ".join(get_cert_element(cert, "subject").split(" ")[1:])


def get_cert_issuer(cert):
    ####################################################################
    """Return the issuer DN of the x509 certificate of the identity"""
    ####################################################################
    # issuer= /C=US/O=Entrust/OU=Certification Authorities/OU=Entrust Managed Services SSP CA
    return " ".join(get_cert_element(cert, "issuer").split(" ")[1:])


def get_cert_enddate(cert):
    ####################################################################
    """Return the issuer DN of the x509 certificate of the identity"""
    ####################################################################
    return get_cert_element(cert, "enddate").split("=")[1]


def get_cert_issuerhash(cert):
    ####################################################################
    """Return the issuer DN of the x509 certificate of the identity"""
    ####################################################################
    return get_cert_element(cert, "issuer_hash")


def get_cert_subjecthash(cert):
    ####################################################################
    """Return the issuer DN of the x509 certificate of the identity"""
    ####################################################################
    return get_cert_element(cert, "subject_hash")


def get_cert_element(cert, element):
    ####################################################################
    """Return an arbitrary element of an x509 certificate"""
    ####################################################################
    command = ["openssl", "x509", "-noout", f"-{element}"]
    if element == "fingerprint":
        command.append("-sha1")
    with Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT) as proc:
        stdout, _ = proc.communicate(input=cert)
        if proc.returncode != 0:
            raise X509CertificateError(stdout)

    try:
        return stdout.decode("UTF-8").rstrip()
    except IndexError as err:
        raise X509CertificateError(stdout) from err


def get_card_element(element, SCBackend, card_slot=None):
    ####################################################################
    """Return an arbitrary element of a pcks15 capable device"""
    ####################################################################
    if SCBackend == "opensc":
        command = ["pkcs15-tool", "--read-certificate", "1"]
        if card_slot is not None:
            command.extend(["--reader", str(card_slot)])
    elif SCBackend == "yubi":
        command = ["yubico-piv-tool", "-a", "read-certificate", "-s", "9a"]
        if card_slot is not None and card_slot != 0:
            command.extend(["-r", str(card_slot)])
    else:
        raise BadBackendError(SCBackend)
    with Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT) as proc:
        stdout, _ = proc.communicate()
    if stdout.decode("utf-8").strip().lower() == "no smart card readers found.":
        raise X509CertificateError("Smartcard not detected")
    return get_cert_element(stdout, element)


def get_card_fingerprint(SCBackend, card_slot=None):
    ####################################################################
    """Return the modulus of the x509 certificate of the identity"""
    ####################################################################
    # SHA1 Fingerprint=F9:9D:71:54:55:BE:99:24:6A:5E:E0:BB:48:F9:63:AE:A2:05:54:98
    return get_card_element("fingerprint", SCBackend, card_slot=card_slot).split("=")[1]


def get_card_subject(SCBackend, card_slot=None):
    ####################################################################
    """Return the subject DN of the x509 certificate of the identity"""
    ####################################################################
    # subject= /C=US/O=Entrust/OU=Certification Authorities/OU=Entrust Managed Services SSP CA
    return " ".join(get_card_element("subject", SCBackend, card_slot=card_slot).split(" ")[1:])


def get_card_issuer(SCBackend, card_slot=None):
    ####################################################################
    """Return the issuer DN of the x509 certificate of the identity"""
    ####################################################################
    # issuer= /C=US/O=Entrust/OU=Certification Authorities/OU=Entrust Managed Services SSP CA
    return " ".join(get_card_element("issuer", SCBackend, card_slot=card_slot).split(" ")[1:])


def get_card_startdate(SCBackend, card_slot=None):
    ####################################################################
    """Return the issuer DN of the x509 certificate of the identity"""
    ####################################################################
    return get_card_element("startdate", SCBackend, card_slot=card_slot).split("=")[1]


def get_card_enddate(SCBackend, card_slot=None):
    ####################################################################
    """Return the issuer DN of the x509 certificate of the identity"""
    ####################################################################
    return get_card_element("enddate", SCBackend, card_slot=card_slot).split("=")[1]


def get_card_issuerhash(SCBackend, card_slot=None):
    ####################################################################
    """Return the issuer DN of the x509 certificate of the identity"""
    ####################################################################
    return get_card_element("issuer_hash", SCBackend, card_slot=card_slot)


def get_card_subjecthash(SCBackend, card_slot=None):
    ####################################################################
    """Return the issuer DN of the x509 certificate of the identity"""
    ####################################################################
    return get_card_element("subject_hash", SCBackend, card_slot=card_slot)


def get_card_serial(card_slot=None):
    ####################################################################
    """Return the serial element of a yubico card"""
    ####################################################################
    command = ["yubico-piv-tool", "-a", "status"]
    if card_slot is not None and card_slot != 0:
        command.extend(["-r", str(card_slot)])
    with Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT) as proc:
        stdout, _ = proc.communicate()
    if stdout.decode("utf-8").strip().lower() == "no smart card readers found.":
        raise X509CertificateError("Smartcard not detected")
    for line in stdout.decode("utf-8").strip().lower().splitlines():
        if "serial number:" in line:
            return line.split(":")[1].replace(" ", "").replace("\t", "")
    raise X509CertificateError("Smartcard not detected")
    return None


def sk_encrypt_string(plaintext_string, key):
    ####################################################################
    """Symmetrically Encrypt and return a base 64 encoded string using the provided secret"""
    ####################################################################
    fern = Fernet(hash_password(key))
    encrypted_string = fern.encrypt(plaintext_string.encode("UTF-8"))
    return urlsafe_b64encode(handle_python_strings(encrypted_string))


def sk_decrypt_string(ciphertext_string, key):
    ####################################################################
    """Symmetrically Decrypt a base64 encoded string using the provided key"""
    ####################################################################
    fern = Fernet(hash_password(key))
    ciphertext_string = handle_python_strings(ciphertext_string)
    try:
        plaintext_string = fern.decrypt(
            urlsafe_b64decode(handle_python_strings(ciphertext_string))
        )
        return plaintext_string.decode("UTF-8")
    except InvalidToken:
        # handle some legacy stuff from NCCS
        try:
            plaintext_string = fern.decrypt(ciphertext_string)
            return plaintext_string.decode("UTF-8")
        except InvalidToken as err:
            raise DecryptionError("Incorrect Password") from err


def hash_password(password):
    ####################################################################
    """Hash people's password"""
    ####################################################################
    password = handle_python_strings(f"{password}")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"salt",
        iterations=100000,
        backend=default_backend(),
    )
    return urlsafe_b64encode(handle_python_strings(kdf.derive(password)))


def puppet_password(eyaml, password):
    ####################################################################
    """Give eyaml password"""
    ####################################################################
    command = [eyaml, "encrypt", "-s", password, "-o", "string"]
    with Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT) as proc:
        stdout, _ = proc.communicate()
    return stdout.decode().strip()

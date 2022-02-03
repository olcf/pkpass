"""This module is used to process the decryption of keys"""
from os import path, unlink, walk
from fnmatch import fnmatch
from tempfile import gettempdir
from libpkpass import LOGGER
from libpkpass.commands.command import Command
from libpkpass.password import PasswordEntry
from libpkpass.errors import (
    PasswordIOError,
    CliArgumentError,
    NotARecipientError,
    DecryptionError,
)
from libpkpass.models.recipient import Recipient


class Show(Command):
    ####################################################################
    """This class is used as a command object and parses information passed through
    the CLI to show passwords that have been distributed to users"""
    ####################################################################
    name = "show"
    description = "Display a password"
    selected_args = Command.selected_args + [
        "all",
        "behalf",
        "card_slot",
        "ignore_decrypt",
        "keypath",
        "nopassphrase",
        "noverify",
        "pwname",
        "pwstore",
        "recovery",
        "stdin",
    ]

    def _run_command_execution(self):
        ####################################################################
        """Run function for class."""
        ####################################################################
        password = PasswordEntry()
        if "behalf" in self.args and self.args["behalf"]:
            yield from self._behalf_prep(password)
        else:
            yield from self._show_wrapper(password)

    def _show_wrapper(self, password):
        ####################################################################
        """Wrapper for show to allow for on behalf of"""
        ####################################################################
        if self.args["all"]:
            try:
                yield from self._walk_dir(password)
            except DecryptionError as err:
                raise err
        elif self.args["pwname"] is None:
            raise PasswordIOError("No password supplied")
        else:
            yield from self._decrypt_wrapper(
                self.args["pwstore"], password, self.args["pwname"]
            )

    def _behalf_prep(self, password):
        ####################################################################
        """Create necessary temporary file for rsa key"""
        ####################################################################
        password.read_password_data(
            path.join(self.args["pwstore"], self.args["behalf"])
        )
        # allows the password to be stored outside the root of the password directory
        self.args["behalf"] = self.args["behalf"].split("/")[-1]
        temp_key = path.join(gettempdir(), f'{self.args["behalf"]}.key')
        plaintext_pw = password.decrypt_entry(
            identity=self.iddb.id,
            passphrase=self.passphrase,
            card_slot=self.args["card_slot"],
        )
        with open(temp_key, "w", encoding="ASCII") as fname:
            fname.write(
                "%s\n%s\n%s"
                % (
                    "-----BEGIN RSA PRIVATE KEY-----",
                    plaintext_pw.replace("-----BEGIN RSA PRIVATE KEY-----", "")
                    .replace(" -----END RSA PRIVATE KEY----", "")
                    .replace(" ", "\n")
                    .strip(),
                    "-----END RSA PRIVATE KEY-----",
                )
            )
        self.args["identity"] = self.args["behalf"]
        self.args["key_path"] = temp_key
        yield from self._show_wrapper(password)
        unlink(temp_key)

    def _walk_dir(self, password):
        ####################################################################
        """Walk our directory searching for passwords"""
        ####################################################################
        # walk returns root, dirs, and files we just need files
        for root, _, pwnames in walk(self.args['pwstore']):
            trim_root = root.replace(self.args["pwstore"], "").lstrip("/")
            for pwname in pwnames:
                if self.args["pwname"] is None or fnmatch(
                    path.join(trim_root, pwname), self.args["pwname"]
                ):
                    try:
                        yield from self._decrypt_wrapper(root, password, pwname)
                    except DecryptionError as err:
                        if self.args['ignore_decrypt']:
                            LOGGER.err(err)
                            continue
                        raise
                    except (NotARecipientError, TypeError):
                        continue

    def _handle_escrow_show(self, password):
        ####################################################################
        """This populates the user's escrow as passwords"""
        ####################################################################
        if password.escrow:
            if self.iddb.id["name"] in password.escrow["recipients"].keys():
                return password.escrow["recipients"][self.iddb.id["name"]]
        return None

    def _decrypt_wrapper(self, directory, password, pwname):
        ####################################################################
        """Decide whether to decrypt normally or for escrow"""
        ####################################################################
        if directory and password and pwname:
            password.read_password_data(path.join(directory, pwname))
            try:
                if self.args["recovery"]:
                    myescrow = self._handle_escrow_show(password)
                    if myescrow:
                        distributor = myescrow["distributor"]
                        password["recipients"][self.iddb.id["name"]] = myescrow
                        yield self._decrypt_password_entry(password, distributor)
                else:
                    distributor = password.recipients[self.iddb.id["name"]][
                        "distributor"
                    ]
                    yield self._decrypt_password_entry(password, distributor)
            except KeyError as err:
                raise NotARecipientError(
                    f"Identity '{self.iddb.id['name']}' is not on the recipient list for password '{pwname}'"
                ) from err

    def _decrypt_password_entry(self, password, distributor):
        ####################################################################
        """This decrypts a given password entry"""
        ####################################################################
        plaintext_pw = password.decrypt_entry(
            identity=self.iddb.id,
            passphrase=self.passphrase,
            card_slot=self.args["card_slot"],
        )
        dist_obj = (
            self.iddb.session.query(Recipient)
            .filter(Recipient.name == distributor)
            .first()
        )
        if (dist_obj and dist_obj.certs) and not self.args["noverify"]:
            result = password.verify_entry(
                self.iddb.id["name"], self.iddb, distributor, dist_obj.certs
            )
            if not result["sigOK"]:
                LOGGER.warning(
                    "Could not verify that %s correctly signed your password entry.",
                    result["distributor"],
                )
            if not result["certOK"]:
                LOGGER.warning(
                    "Could not verify the certificate authenticity of user '%s'.",
                    result["distributor"],
                )

        return f"{self.color_print(password.metadata['name'], 'first_level')}: {plaintext_pw}"

    def _validate_args(self):
        for argument in ["keypath"]:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(f"'{argument}' is a required argument")

    def _pre_check(self):
        """Ensure our password exists before asking for authentication"""
        for root, _, pwnames in walk(self.args['pwstore']):
            trim_root = root.replace(self.args["pwstore"], "").lstrip("/")
            for pwname in pwnames:
                if self.args["pwname"] is None or fnmatch(
                    path.join(trim_root, pwname), self.args["pwname"]
                ):
                    return True
        raise PasswordIOError(
            f"{path.join(self.args['pwstore'], self.args['pwname'])} does not exist"
        )

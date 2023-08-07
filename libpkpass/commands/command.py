"""This module is a generic for all pkpass commands"""
import getpass
from os import getcwd, path, sep
from sqlalchemy.orm import sessionmaker
from libpkpass import LOGGER
from libpkpass.commands.arguments import ARGUMENTS as arguments
from libpkpass.crypto import print_card_info
from libpkpass.errors import (
    CliArgumentError,
    PasswordIOError,
    NotThePasswordOwnerError,
)
from libpkpass.identities import IdentityDB
from libpkpass.passworddb import PasswordDB
from libpkpass.password import PasswordEntry
from libpkpass.util import collect_args, color_prepare, build_recipient_list
from libpkpass.models.recipient import Recipient


class Command:
    ##########################################################################
    """Base class for all commands.  Auotmatically registers with cli subparser
    and provides run execution for itself."""
    ##########################################################################
    name = None
    description = None
    selected_args = [
        "nocache",
        "verbosity",
        "quiet",
        "identity",
        "cabundle",
        "certpath",
        "color",
        "theme_map",
    ]
    passphrase = None

    def __init__(self, cli, iddb=None, pwdb=None):
        ##################################################################
        """Intialization function for class. Register with argparse"""
        ##################################################################
        # default certpath to none because connect string is allowed
        self.args = {}
        self.recipient_list = []
        self.escrow_and_recipient_list = []
        self.iddb = iddb if iddb else IdentityDB()
        self.pwdbcached = pwdb is not None
        self.passworddb = pwdb if pwdb else PasswordDB()
        cli.register(self, self.name, self.description)

    def register(self, parser):
        ##################################################################
        """Registration function for class. Register with argparse"""
        ##################################################################
        for arg in sorted(self.selected_args):
            parser.add_argument(*arguments[arg]["args"], **arguments[arg]["kwargs"])

    def run(self, parsedargs):
        ##################################################################
        """Passes the argparse Namespace object of parsed arguments"""
        ##################################################################
        self._run_command_setup(parsedargs)
        self._pre_check()
        self._passphrase_check()
        return self._run_command_execution()

    def _passphrase_check(self):
        if "nopassphrase" in self.selected_args and not self.args["nopassphrase"]:
            for mesg in print_card_info(
                self.args["card_slot"],
                self.iddb.id,
                self.args["verbosity"],
                self.args["color"],
                self.args["theme_map"],
                self.args["SCBackend"],
            ):
                LOGGER.info(mesg)
            self.passphrase = getpass.getpass("Enter Pin/Passphrase: ")

    def _run_command_setup(self, parsedargs):
        ##################################################################
        """Passes the argparse Namespace object of parsed arguments"""
        ##################################################################
        self.args = collect_args(parsedargs)
        self.iddb.session = sessionmaker(bind=self.args["db"]["engine"])()
        self._validate_combinatorial_args()
        self._validate_args()

        # Build the list of recipients that this command will act on
        self.recipient_list, self.escrow_and_recipient_list = build_recipient_list(self.args)

        # If there are defined repositories of keys and certificates, load them
        self.iddb.args = self.args
        self.iddb.cabundle = self.args["cabundle"]
        self.iddb.load_certs_from_directory(
            self.args["certpath"],
            connectmap=self.args["connect"],
            nocache=self.args["no_cache"],
        )
        if self.args["keypath"]:
            self.iddb.load_keys_from_directory(self.args["keypath"])
        self.iddb.id = (
            self.iddb.session.query(Recipient)
            .filter(Recipient.name == self.args["identity"])
            .first()
        )
        self._validate_identities()
        self.iddb.id = dict(self.iddb.id)

        if (
            self.args["subparser_name"]
            in ["list", "interpreter", "distribute", "export"]
            and not self.pwdbcached
        ):
            self.passworddb.load_from_directory(self.args["pwstore"])
        if "pwname" in self.args and self.args["pwname"]:
            self._resolve_directory_path()
        self.args["card_slot"] = self.args["card_slot"] if self.args["card_slot"] else 0

    def _resolve_directory_path(self):
        ####################################################################
        """This handles how a user inputs the pwname, this tries to be smart
        good luck everybody else"""
        ####################################################################
        pwd = getcwd()
        pwd_pwname = path.normpath(path.join(pwd, self.args["pwname"]))
        if self.args["pwstore"] in pwd_pwname:
            self.args["pwname"] = pwd_pwname.replace(self.args["pwstore"] + sep, "")

    def safety_check(self):
        ##################################################################
        """This provides a sanity check that you are the owner of a password."""
        ##################################################################
        try:
            password = PasswordEntry()
            password.read_password_data(
                path.join(self.args["pwstore"], self.args["pwname"])
            )
            return (
                self.args["identity"] in password["recipients"],
                password["metadata"]["creator"],
            )
        except PasswordIOError:
            return (True, None)

    def update_pass(self, pass_value):
        ##################################################################
        """Fully updated a password record"""
        ##################################################################
        pass_entry = PasswordEntry()
        pass_entry.read_password_data(
            path.join(self.args["pwstore"], self.args["pwname"])
        )
        swap_pass = PasswordEntry()
        swap_pass.add_recipients(
            secret=pass_value,
            distributor=self.args["identity"],
            recipients=[self.args["identity"]],
            session=self.iddb.session,
            passphrase=self.passphrase,
            card_slot=self.args["card_slot"],
            escrow_users=self.args["escrow_users"],
            minimum=self.args["min_escrow"],
            SCBackend=self.args["SCBackend"],
        )
        pass_entry["recipients"][self.args["identity"]] = swap_pass["recipients"][
            self.args["identity"]
        ]
        pass_entry.write_password_data(
            path.join(self.args["pwstore"], self.args["pwname"]),
            overwrite=self.args["overwrite"],
        )

    def create_pass(self, password1, description, authorizer, recipient_list=None):
        ##################################################################
        """This writes password data to a file."""
        ##################################################################
        password_metadata = {}
        password_metadata["description"] = description
        password_metadata["authorizer"] = authorizer
        password_metadata["creator"] = self.args["identity"]
        password_metadata["name"] = self.args["pwname"]
        if self.args["noescrow"]:
            self.args["min_escrow"] = None
            self.args["escrow_users"] = None
        if recipient_list is None:
            recipient_list = [self.args["identity"]]

        password = PasswordEntry(**password_metadata)

        password.add_recipients(
            secret=password1,
            distributor=self.args["identity"],
            recipients=recipient_list,
            session=self.iddb.session,
            passphrase=self.passphrase,
            card_slot=self.args["card_slot"],
            escrow_users=self.args["escrow_users"],
            minimum=self.args["min_escrow"],
            SCBackend=self.args["SCBackend"],
        )

        password.write_password_data(
            path.join(self.args["pwstore"], self.args["pwname"]),
            overwrite=self.args["overwrite"],
        )

    def create_or_update_pass(
        self, password1, description, authorizer, recipient_list=None
    ):
        ##################################################################
        """This creates new or updates existing passwords"""
        ##################################################################
        safe, owner = self.safety_check()
        if safe or self.args["overwrite"]:
            if owner and owner != self.args["identity"]:
                self.update_pass(password1)
            else:
                self.create_pass(password1, description, authorizer, recipient_list)
        else:
            raise NotThePasswordOwnerError(
                self.args["identity"], owner, self.args["pwname"]
            )

    def _run_command_execution(self):
        ##################################################################
        """Passes the argparse Namespace object of parsed arguments"""
        ##################################################################
        raise NotImplementedError

    def _validate_args(self):
        raise NotImplementedError

    def _pre_check(self):
        """Pre check likely won't happen on all commands so we'll allow a
        pass"""

    def _validate_combinatorial_args(self):
        ##################################################################
        """This is a weird function name so: combinatorial in this case
        means that one of the 'combinatorial' arguments are required
        however, not all of them are necessarily required.
        Ex: We need certs, we can get this from certpath or connect
        we do not need both of these arguments but at least one is
        required"""
        ##################################################################
        # we want a multi-dim of lists, this way if more combinations come up
        # that would be required in a 1 or more capacity, we just add
        # a list to this list
        args_list = [["certpath", "connect"]]
        for arg_set in args_list:
            valid = False
            for arg in arg_set:
                if arg in self.args and self.args[arg] is not None:
                    valid = True
                    break
            if not valid:
                raise CliArgumentError(f"'{arg_set[0]}' or '{arg_set[1]}' is required")

    def _validate_identities(self, swap_list=None):
        ##################################################################
        """Ensure identities meet criteria for processing"""
        ##################################################################
        if not swap_list:
            swap_list = self.escrow_and_recipient_list
        for recipient in swap_list:
            self.iddb.verify_identity(recipient)
            if recipient not in [
                x[0] for x in self.iddb.session.query(Recipient.name).all()
            ]:
                raise CliArgumentError(
                    f"Error: Recipient '{recipient}' is not in the recipient database"
                )

        if self.iddb.id:
            self.iddb.verify_identity(self.args["identity"])
        else:
            raise CliArgumentError(
                f"Error: Your user '{self.args['identity']}' is not in the recipient database"
            )

    def color_print(self, string, color_type):
        ##################################################################
        """Handle the color printing for objects"""
        ##################################################################
        return color_prepare(
            string, color_type, self.args["color"], self.args["theme_map"]
        )

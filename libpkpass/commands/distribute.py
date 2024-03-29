"""This Modules allows for distributing created passwords to other users"""
from os import path
from tqdm import tqdm
from libpkpass import LOGGER
from libpkpass.util import dictionary_filter, sort
from libpkpass.commands.command import Command
from libpkpass.password import PasswordEntry
from libpkpass.errors import CliArgumentError
from libpkpass.models.recipient import Recipient


class Distribute(Command):
    ####################################################################
    """This Class implements the CLI functionality for ditribution"""
    ####################################################################
    name = "distribute"
    description = "Distribute existing password entry/ies to another entity [matching uses python fnmatch]"
    selected_args = Command.selected_args + [
        "pwname",
        "pwstore",
        "users",
        "groups",
        "stdin",
        "min_escrow",
        "escrow_users",
        "keypath",
        "nopassphrase",
        "nosign",
        "card_slot",
        "noescrow",
    ]

    def __init__(self, *args, **kwargs):
        Command.__init__(self, *args, **kwargs)
        self.filtered_pdb = {}

    def _run_command_execution(self):
        ####################################################################
        """Run function for class."""
        ####################################################################
        yield from self._confirm_pdb()
        self.recipient_list.append(str(self.args["identity"]))
        self.recipient_list = list(set(self.recipient_list))
        yield from self._confirm_recipients()
        for dist_pass, _ in tqdm(self.filtered_pdb.items()):
            password = PasswordEntry()
            password.read_password_data(dist_pass)
            if self.args["identity"] in password.recipients.keys():
                plaintext_pw = password.decrypt_entry(
                    self.iddb.id,
                    passphrase=self.passphrase,
                    card_slot=self.args["card_slot"],
                    SCBackend=self.args["SCBackend"],
                    PKCS11_module_path=self.args["PKCS11_module_path"],
                )
                password.add_recipients(
                    secret=plaintext_pw,
                    distributor=self.args["identity"],
                    recipients=self.recipient_list,
                    session=self.iddb.session,
                    passphrase=self.passphrase,
                    card_slot=self.args["card_slot"],
                    escrow_users=self.args["escrow_users"],
                    minimum=self.args["min_escrow"],
                    SCBackend=self.args["SCBackend"],
                    PKCS11_module_path=self.args["PKCS11_module_path"],
                )

                password.write_password_data(dist_pass)

    def _validate_args(self):
        for argument in ["pwname", "keypath"]:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(f"'{argument}' is a required argument")

    def _confirm_pdb(self):
        self.filtered_pdb = dictionary_filter(
            path.join(self.args["pwstore"], self.args["pwname"]),
            self.passworddb.pwdb,
            [self.args["identity"], "recipients"],
        )
        yield "The following password files have matched:"
        yield "\n".join(self.filtered_pdb.keys())
        correct = input("Are these correct? (y/N) ")
        if not correct or correct.lower()[0] == "n":
            self.args["pwname"] = input("Please try a new filter: ")
            yield from self._confirm_pdb()

    def _confirm_recipients(self):
        not_in_db = []
        in_db = [x.name for x in self.iddb.session.query(Recipient).all()]
        for recipient in self.recipient_list:
            if recipient not in in_db:
                not_in_db.append(recipient)
        if not_in_db:
            LOGGER.warning(
                "The following recipients are not in the db, removing %s",
                ", ".join(not_in_db),
            )
            self.recipient_list = [x for x in self.recipient_list if x not in not_in_db]
        yield "The following user(s) will be added: "
        yield ", ".join(sort(self.recipient_list))
        correct = input("Are these correct? (y/N) ")
        if not correct or correct.lower()[0] == "n":
            self.recipient_list = input("Please enter a comma delimited list: ")
            self.recipient_list = list(
                {x.strip() for x in self.recipient_list.split(",")}
            )
            yield from self._confirm_recipients()

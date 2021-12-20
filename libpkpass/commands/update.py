"""This module allows for the updating of passwords"""
import getpass
from os import path
from libpkpass import LOGGER
from libpkpass.util import sort
from libpkpass.password import PasswordEntry
from libpkpass.commands.command import Command
from libpkpass.errors import CliArgumentError, PasswordMismatchError, NotThePasswordOwnerError,\
        BlankPasswordError
from libpkpass.models.recipient import Recipient

    ####################################################################
class Update(Command):
    """This class implements the CLI functionality of updating existing passwords"""
    ####################################################################
    name = 'update'
    description = 'Change a password value and redistribute to recipients'
    selected_args = Command.selected_args + ['pwname', 'pwstore', 'overwrite', 'stdin', 'keypath',
                                             'nopassphrase', 'nosign', 'card_slot', 'escrow_users',
                                             'min_escrow', 'noescrow']

        ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                      """
        ####################################################################
        password = PasswordEntry()
        password.read_password_data(path.join(
            self.args['pwstore'], self.args['pwname']))
        safe, owner = self.safety_check()
        if safe or self.args['overwrite']:
            self.recipient_list = password['recipients'].keys()
            yield from self._confirm_recipients()
            self._validate_identities(self.recipient_list)

            password1 = getpass.getpass("Enter updated password: ")
            if password1.strip() == "":
                raise BlankPasswordError
            password2 = getpass.getpass("Enter updated password again: ")
            if password1 != password2:
                raise PasswordMismatchError

            # This is due to a poor naming convention; we don't want to go through the
            # create or update, because we are not updating a single record in the yaml
            # we are burning it to the ground and redoing the entire thing
            self.create_pass(password1,
                             password['metadata']['description'],
                             password['metadata']['authorizer'],
                             self.recipient_list)
        else:
            raise NotThePasswordOwnerError(self.args['identity'], owner, self.args['pwname'])

        ####################################################################
    def _confirm_recipients(self):
        ####################################################################
        not_in_db = []
        in_db = [x.name for x in self.session.query(Recipient).all()]
        for recipient in self.recipient_list:
            if recipient not in in_db:
                not_in_db.append(recipient)
        if not_in_db:
            LOGGER.warning(
                "The following recipients are not in the db, removing %s", ', '.join(not_in_db)
            )
            self.recipient_list = [x for x in self.recipient_list if x not in not_in_db]
        yield "The following users will receive the password: "
        yield ", ".join(sort(self.recipient_list))
        correct = input("Are these correct? (y/N) ")
        if not correct or correct.lower()[0] == 'n':
            self.recipient_list = input("Please enter a comma delimited list: ")
            self.recipient_list = list({x.strip() for x in self.recipient_list.split(",")})
            yield from self._confirm_recipients()

        ####################################################################
    def _validate_args(self):
        ####################################################################
        for argument in ['pwname', 'keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(f"'{argument}' is a required argument")

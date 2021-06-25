"""This Modules allows for distributing created passwords to other users"""
from os import path
from tqdm import tqdm
import libpkpass.util as util
from libpkpass.commands.command import Command
from libpkpass.password import PasswordEntry
from libpkpass.errors import CliArgumentError

    ####################################################################
class Distribute(Command):
    """This Class implements the CLI functionality for ditribution"""
    ####################################################################
    name = 'distribute'
    description = 'Distribute existing password entry/ies to another entity [matching uses python fnmatch]'
    selected_args = Command.selected_args + ['pwname', 'pwstore', 'users', 'groups', 'stdin',
                                             'min_escrow', 'escrow_users', 'keypath', 'nopassphrase',
                                             'nosign', 'card_slot', 'noescrow']

        ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                      """
        ####################################################################
        filtered_pdb = util.dictionary_filter(
            path.join(self.args['pwstore'], self.args['pwname']),
            self.passworddb.pwdb,
            [self.args['identity'], 'recipients']
        )
        self.recipient_list.append(str(self.args['identity']))
        self.recipient_list = list(set(self.recipient_list))
        print("The following users will receive the password:")
        print(", ".join(self.recipient_list))
        print("The following password files have matched:")
        print(*filtered_pdb.keys(), sep="\n")
        correct_distribution = input("Are these lists correct? (y/N) ")
        if correct_distribution and correct_distribution.lower()[0] == 'y':
            self.passworddb.pwdb = filtered_pdb
            for dist_pass, _ in tqdm(self.passworddb.pwdb.items()):
                password = PasswordEntry()
                password.read_password_data(dist_pass)
                if self.args['identity'] in password.recipients.keys():
                    # we shouldn't modify escrow on distribute
                    self.args['min_escrow'] = None
                    self.args['escrow_users'] = None
                    plaintext_pw = password.decrypt_entry(
                        self.identities.iddb[self.args['identity']],
                        passphrase=self.passphrase,
                        card_slot=self.args['card_slot'])

                    password.read_password_data(dist_pass)
                    password.add_recipients(secret=plaintext_pw,
                                            distributor=self.args['identity'],
                                            recipients=self.recipient_list,
                                            identitydb=self.identities,
                                            passphrase=self.passphrase,
                                            card_slot=self.args['card_slot'],
                                            pwstore=self.args['pwstore']
                                           )

                    password.write_password_data(dist_pass)
        else:
            print("Exiting due to wrong password list")

        ####################################################################
    def _validate_args(self):
        ####################################################################
        for argument in ['pwname', 'keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)

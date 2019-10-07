"""This module allows for inspecting metadata passwords"""
import os
import datetime
from libpkpass.password import PasswordEntry
from libpkpass.commands.command import Command
from libpkpass.errors import CliArgumentError


    ####################################################################
class Info(Command):
    """This class implements the CLI functionality of creation of passwords"""
    ####################################################################
    name = 'info'
    description = 'Create a new password entry and encrypt it for yourself'
    selected_args = Command.selected_args + ['pwname', 'pwstore']

        ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                      """
        ####################################################################
        password = PasswordEntry()
        password.read_password_data(os.path.join(self.args['pwstore'], self.args['pwname']))

        # Metadata
        print(self.color_print("Metadata:", "first_level"))
        for key, value in password.metadata.items():
            print("  %s: %s" % (self.color_print(key.capitalize(), "second_level"),
                                value))

        # Escrow
        if password.escrow:
            print(self.color_print("\nEscrow Groups:", "first_level"))
            for group_key, group_value in password.escrow.items():
                print("  %s:" % self.color_print(group_key, "second_level"))
                for key, value in group_value['metadata'].items():
                    print("    %s %s" % (self.color_print(key + ":", "third_level"), str(value)))

                print("    %s %s" % (self.color_print("Share Holders:", "third_level"),
                                     ', '.join(list(group_value['recipients'].keys()))))
                print("    %s %s" % (self.color_print("Total Group Share Holders:", "third_level"),
                                     len(list(group_value['recipients'].keys()))))

                timestamp = int(round(float(min([x['timestamp'] for x in list(group_value['recipients'].values()) if 'timestamp' in x]))))
                timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                print("    %s %s" % (self.color_print("Group creation time:", "third_level"),
                                     timestamp))

        # Recipients
        print("%s %s" % (self.color_print("\nRecipients:", "first_level"),
                         ', '.join(list(password.recipients.keys()))))
        print("%s %s" % (self.color_print("Total Recipients:", "first_level"),
                         len(list(password.recipients.keys()))))
        rec_timestamp = int(round(float(min([x['timestamp'] for x in list(password.recipients.values()) if 'timestamp' in x]))))
        rec_timestamp = datetime.datetime.fromtimestamp(rec_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        print("%s %s" % (self.color_print("Earliest distribute timestamp:", "first_level"),
                         rec_timestamp))

        ####################################################################
    def _validate_args(self):
        ####################################################################
        for argument in ['pwname', 'keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)

"""This module allows for inspecting metadata passwords"""
from os import path, linesep
from datetime import datetime
from libpkpass.password import PasswordEntry
from libpkpass.commands.command import Command
from libpkpass.errors import CliArgumentError

    ####################################################################
class Info(Command):
    """This class implements the display of metadata to users"""
    ####################################################################
    name = 'info'
    description = 'Displays metadata about a password'
    selected_args = Command.selected_args + ['pwname', 'pwstore']

        ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                      """
        ####################################################################
        password = PasswordEntry()
        password.read_password_data(path.join(self.args['pwstore'], self.args['pwname']))

        # Metadata
        yield self.color_print("Metadata:", "first_level")
        for key, value in password.metadata.items():
            yield f"  {self.color_print(key.capitalize(), 'second_level')}: {value}"

        # Escrow
        if password.escrow:
            yield self.color_print("\nEscrow Groups:", "first_level")
            for group_key, group_value in password.escrow.items():
                yield f"  {self.color_print(group_key, 'second_level')}:"
                for key, value in group_value['metadata'].items():
                    yield f"    {self.color_print(key + ':', 'third_level')} {str(value)}"

                yield f"    {self.color_print('Share Holders:', 'third_level')} {', '.join(list(group_value['recipients'].keys()))}"
                yield f"    {self.color_print('Total Group Share Holders:', 'third_level')} {len(list(group_value['recipients'].keys()))}"

                timestamp_list = [x['timestamp'] for x in list(group_value['recipients'].values()) if 'timestamp' in x]
                if timestamp_list:
                    timestamp = int(round(float(min(timestamp_list))))
                    timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    yield f"    {self.color_print('Group creation time:', 'third_level')} {timestamp}"

        # Recipients
        yield f"{self.color_print(linesep + 'Recipients:', 'first_level')} {', '.join(list(password.recipients.keys()))}"
        yield f"{self.color_print('Total Recipients:', 'first_level')} {len(list(password.recipients.keys()))}"
        rec_timestamp = int(round(float(min([x['timestamp'] for x in list(password.recipients.values()) if 'timestamp' in x]))))
        rec_timestamp = datetime.fromtimestamp(rec_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        yield f"{self.color_print('Earliest distribute timestamp:', 'first_level')} {rec_timestamp}"

        ####################################################################
    def _validate_args(self):
        ####################################################################
        for argument in ['pwname', 'keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(f"'{argument}' is a required argument")

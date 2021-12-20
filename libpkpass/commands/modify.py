"""This Module allows for editing metadata of passwords"""
from os import path
from libpkpass.commands.command import Command
from libpkpass.password import PasswordEntry
from libpkpass.errors import CliArgumentError

    ####################################################################
class Modify(Command):
    """This class implements the cli list"""
    ####################################################################
    name = 'modify'
    description = 'Modify the metadata of a password'
    selected_args = Command.selected_args + ['pwname', 'pwstore']

        ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                      """
        ####################################################################
        full_path = path.join(self.args['pwstore'], self.args['pwname'])
        password = PasswordEntry()
        password.read_password_data(full_path)
        editable = ['authorizer', 'description']
        for key, value in password['metadata'].items():
            if key in editable:
                yield f'''{self.color_print(f"Current value for '{key}':", "first_level")} {value}'''
                password['metadata'][key] = input(f"New Value for {key}: ")

        password.write_password_data(full_path)

        ####################################################################
    def _validate_args(self):
        ####################################################################
        for argument in ['pwname', 'pwstore']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(f"'{argument}' is a required argument")

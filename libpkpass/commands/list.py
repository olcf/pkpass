"""This Module allows for the listing of users passwords"""

from __future__ import print_function
import yaml
from libpkpass.commands.command import Command
from libpkpass.passworddb import PasswordDB
from libpkpass.errors import CliArgumentError


class List(Command):
    """This class implements the cli list"""
    name = 'list'
    description = 'List passwords you have access to'
    selected_args = Command.selected_args + ['pwstore', 'stdin', 'recovery']

    def _run_command_execution(self):
        ####################################################################
        """ Run function for class.                                      """
        ####################################################################

        passworddb = PasswordDB()
        passworddb.load_from_directory(self.args['pwstore'])

        result = {}
        for pwname, passwordentry in passworddb.pwdb.items():
            if self.args['recovery']:
                if passwordentry.escrow:
                    for rec_list in passwordentry.escrow.keys():
                        recipients = passwordentry.escrow[rec_list]['recipients']
                        for key, value in recipients.items():
                            if key == self.args['identity']:
                                result[pwname] = {
                                    'name': passwordentry.metadata['name'],
                                    'group': rec_list,
                                    'stake_holders': recipients.keys(),
                                    'distributor': value['distributor'],
                                    'minimum_shares': passwordentry.escrow[rec_list]['metadata']['minimum_escrow']
                                }
            elif self.args['identity'] in passwordentry.recipients.keys():
                result[pwname] = {
                    'name': passwordentry.metadata['name'],
                    'distributor': passwordentry.recipients[self.args['identity']]['distributor']
                }


        print("Passwords for '%s':" % self.args['identity'])
        print("\n%s" % yaml.dump(result, default_flow_style=False))

    def _validate_args(self):
        for argument in ['keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)

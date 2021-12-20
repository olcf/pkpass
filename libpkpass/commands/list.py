"""This Module allows for the listing of users passwords"""
from libpkpass.util import dictionary_filter
from libpkpass.commands.command import Command
from libpkpass.errors import CliArgumentError

    ####################################################################
class List(Command):
    """This class implements the cli list"""
    ####################################################################
    name = 'list'
    description = 'List passwords you have access to'
    selected_args = Command.selected_args + ['pwstore', 'stdin', 'recovery', 'filter']

        ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                      """
        ####################################################################
        result = {}
        for pwname, passwordentry in self.passworddb.pwdb.items():
            if self.args['recovery'] and passwordentry.escrow:
                for rec_list in passwordentry.escrow.keys():
                    recipients = passwordentry.escrow[rec_list]['recipients']
                    for key, value in recipients.items():
                        if key == self.args['identity']:
                            result[pwname] = {
                                'name': passwordentry.metadata['name'],
                                'group': rec_list,
                                'stake_holders': list(recipients.keys()),
                                'distributor': value['distributor'],
                                'minimum_shares': passwordentry.escrow[rec_list]['metadata']['minimum_escrow']
                            }
            elif not self.args['recovery'] and self.args['identity'] in passwordentry.recipients.keys():
                result[pwname] = {
                    'name': passwordentry.metadata['name'],
                    'distributor': passwordentry.recipients[self.args['identity']]['distributor']
                }

        if 'filter' in self.args and self.args['filter']:
            result = dictionary_filter(self.args['filter'], result)

        yield f"Passwords for '{self.args['identity']}':"
        for key, value in sorted(result.items()):
            yield f"{self.color_print(key + ':', 'first_level')}\n  {self.color_print('Distributor: ', 'second_level') + value['distributor']}\n  {self.color_print('Name: ', 'second_level') + value['name']}"

        ####################################################################
    def _validate_args(self):
        ####################################################################
        for argument in ['keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(f"'{argument}' is a required argument")

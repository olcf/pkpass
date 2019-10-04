"""This Module allows for the listing of users passwords"""
from libpkpass.commands.command import Command
from libpkpass.crypto import print_card_info


class Card(Command):
    """This class implements the cli list"""
    name = 'card'
    description = 'List the available cards and which card you have selected'
    selected_args = Command.selected_args

    ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                  """
    ####################################################################
        print_card_info(self.args['card_slot'],
                        self.args['identity'],
                        2,
                        self.args['color'])

    ####################################################################
    def _validate_args(self):
    ####################################################################
        pass

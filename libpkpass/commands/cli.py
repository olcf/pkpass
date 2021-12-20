#!/usr/bin/env python3
"""This Module implements a CLI"""
from libpkpass.util import show_version
from libpkpass.commands.pkinterface import PkInterface
from libpkpass.commands.interpreter import Interpreter

    ##############################################################################
class Cli(PkInterface):
    """ Class for parsing command line.  Observes subclasses of Command to Register
    those commands in the actions list.                                        """
    ##############################################################################

        ####################################################################
    def __init__(self):
        """ Intialization function for class. Register all subcommands   """
        ####################################################################
        PkInterface.__init__(self)

        Interpreter(self)
        self.parser.add_argument(
            '--version', action='store_true', help='Show the version of PkPass and exit')

        self.parser.set_default_subparser(self.parser, name='interpreter')
        self.parsedargs = self.parser.parse_args()

    def run(self):
        if 'version' in self.parsedargs and self.parsedargs.version:
            return show_version()
        return self.actions[self.parsedargs.subparser_name].run(self.parsedargs)

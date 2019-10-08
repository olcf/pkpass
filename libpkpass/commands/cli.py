#!/usr/bin/env python
"""This Module implements a CLI"""

from __future__ import print_function
import libpkpass.util as util
import libpkpass.commands.pkinterface as pkinterface
import libpkpass.commands.interpreter as interpreter

    ##############################################################################
class Cli(pkinterface.PkInterface):
    """ Class for parsing command line.  Observes subclasses of Command to Register
    those commands in the actions list.                                        """
    ##############################################################################

        ####################################################################
    def __init__(self):
        """ Intialization function for class. Register all subcommands   """
        ####################################################################
        pkinterface.PkInterface.__init__(self)

        interpreter.Interpreter(self)
        self.parser.add_argument(
            '--version', action='store_true', help='Show the version of PkPass and exit')

        self.parser.set_default_subparser(self.parser, name='interpreter')
        self.parsedargs = self.parser.parse_args()
        if 'version' in self.parsedargs and self.parsedargs.version:
            print(util.show_version())
        else:
            self.actions[self.parsedargs.subparser_name].run(self.parsedargs)

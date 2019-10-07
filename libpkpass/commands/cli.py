#!/usr/bin/env python
"""This Module implements a CLI"""

from __future__ import print_function
import argparse
import os
import libpkpass.util as util
import libpkpass.commands.card as card
import libpkpass.commands.clip as clip
import libpkpass.commands.create as create
import libpkpass.commands.delete as delete
import libpkpass.commands.distribute as distribute
import libpkpass.commands.export as export
import libpkpass.commands.fileimport as pkimport
import libpkpass.commands.generate as generate
import libpkpass.commands.interpreter as interpreter
import libpkpass.commands.list as pklist
import libpkpass.commands.listrecipients as listrecipients
import libpkpass.commands.recover as recover
import libpkpass.commands.rename as rename
import libpkpass.commands.show as show
import libpkpass.commands.update as update

    ##############################################################################
class Cli():
    """ Class for parsing command line.  Observes subclasses of Command to Register
    those commands in the actions list.                                        """
    ##############################################################################

        ####################################################################
    def __init__(self):
        """ Intialization function for class. Register all subcommands   """
        ####################################################################
        # Hash of registered subparser actions, mapping string to actual subparser
        self.actions = {}
        home = os.path.expanduser("~")
        self.parser = argparse.ArgumentParser(
            description='Public Key Password Manager')
        self.parser.set_default_subparser = util.set_default_subparser
        self.parser.add_argument(
            '--config', type=str, help="Path to a PKPass configuration file.  Defaults to '~/.pkpassrc'",
            default=os.path.join(home, '.pkpassrc'))
        self.parser.add_argument(
            '--version', action='store_true', help='Show the version of PkPass and exit')
        self.subparsers = self.parser.add_subparsers(
            help='sub-commands', dest='subparser_name')

        card.Card(self)
        clip.Clip(self)
        create.Create(self)
        delete.Delete(self)
        distribute.Distribute(self)
        export.Export(self)
        generate.Generate(self)
        pkimport.Import(self)
        interpreter.Interpreter(self)
        pklist.List(self)
        listrecipients.Listrecipients(self)
        recover.Recover(self)
        rename.Rename(self)
        show.Show(self)
        update.Update(self)

        self.parser.set_default_subparser(self.parser, name='interpreter')
        self.parsedargs = self.parser.parse_args()
        if 'version' in self.parsedargs and self.parsedargs.version:
            print(util.show_version())
        else:
            self.actions[self.parsedargs.subparser_name].run(self.parsedargs)

        ####################################################################
    def register(self, command_obj, command_name, command_description):
        """ Register command objects and names using an observer pattern """
        ####################################################################
        self.actions[command_name] = command_obj
        parser = self.subparsers.add_parser(
            command_name, help=command_description)
        command_obj.register(parser)

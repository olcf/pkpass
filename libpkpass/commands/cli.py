#!/usr/bin/env python
"""This Module implements a CLI"""

from __future__ import print_function
import argparse
import os
import sys
from cmd2 import Cmd, with_argparser
from libpkpass.commands.command import Command
import libpkpass.commands.clip as clip
import libpkpass.commands.create as create
import libpkpass.commands.delete as delete
import libpkpass.commands.distribute as distribute
import libpkpass.commands.export as export
import libpkpass.commands.fileimport as pkimport
import libpkpass.commands.generate as generate
# import libpkpass.commands.interpreter as interpreter
import libpkpass.commands.list as pklist
import libpkpass.commands.listrecipients as listrecipients
import libpkpass.commands.recover as recover
import libpkpass.commands.rename as rename
import libpkpass.commands.show as show
import libpkpass.commands.update as update

####################################################################
def set_default_subparser(self, name, args=None, positional_args=0):
    """Set default subparser to interpreter"""
####################################################################
    subparser_found = False
    for arg in sys.argv[1:]:
        if arg in ['-h', '--help']:
            break
    else:
        for action in self._subparsers._actions:
            if not isinstance(action, argparse._SubParsersAction):
                continue
            for _ in sys.argv[1:]:
                subparser_found = True
        if not subparser_found:
            if args is None:
                sys.argv.insert(len(sys.argv) - positional_args, name)
            else:
                args.insert(len(args) - positional_args, name)

class PkParse(argparse.ArgumentParser):
    def __init__(self, **kwargs):
        argparse.ArgumentParser.__init__(self, **kwargs)
        home = os.path.expanduser("~")
        self.subparsers = self.add_subparsers(help='sub-commands',
                                              dest='subparser_name')
        self.add_argument(
            '--config', type=str, help="Path to a PKPass configuration file.  Defaults to '~/.pkpassrc'",
            default=os.path.join(home, '.pkpassrc'))


##############################################################################
class Cli(object, Cmd):
    """ Class for parsing command line.  Observes subclasses of Command to Register
    those commands in the actions list.                                        """
##############################################################################
    prompt = 'pkpass> '
    intro = "Welcome! Type ? to list commands"

    ####################################################################
    def __init__(self, loop=False):
        """ Intialization function for class. Register all subcommands   """
    ####################################################################
        # Hash of registered subparser actions, mapping string to actual subparser
        Cmd.__init__(self)
        self.actions = {}
        self.parser = PkParse(description='Public Key Password Manager')
        self.subparsers = self.parser.subparsers
        self.parser.set_default_subparser = set_default_subparser

        clip.Clip(self)
        create.Create(self)
        delete.Delete(self)
        distribute.Distribute(self)
        export.Export(self)
        generate.Generate(self)
        pkimport.Import(self)
        Interpreter(self)
        pklist.List(self)
        listrecipients.Listrecipients(self)
        recover.Recover(self)
        rename.Rename(self)
        show.Show(self)
        update.Update(self)

        self.parser.set_default_subparser(self.parser, name='interpreter')
        self.parsedargs = self.parser.parse_args()
        if not loop:
            self.actions[self.parsedargs.subparser_name].run(self.parsedargs)

    ####################################################################
    def do_exit(self, inp):
        """Exit the application"""
    ####################################################################
        print("Bye")
        return True

    ####################################################################
    def default(self, line):
    ####################################################################
        if "interpreter" in line.lower():
            return False

    @with_argparser(PkParse(description='PkPass interactive commandline'))
    def do_create(self, line):
        print(self.parsedargs)
        print("help")
        self.actions['create'].run(self.parsedargs)

    ####################################################################
    def register(self, command_obj, command_name, command_description):
        """ Register command objects and names using an observer pattern """
    ####################################################################
        self.actions[command_name] = command_obj
        parser = self.subparsers.add_parser(
            command_name, help=command_description)
        command_obj.register(parser)

class Interpreter(Command):
    """This class implements a skeleton to call the interpreter"""
    name = 'interpreter'
    description = 'Interactive mode for pkpass'
    selected_args = ['cabundle', 'card_slot', 'certpath', 'connect', 'escrow_users', 'min_escrow',
                     'groups', 'identity', 'keypath', 'pwstore']

    def _run_command_execution(self):
        ####################################################################
        """ Run function for class.                                      """
        ####################################################################
        print("hi")
        Cli(True).cmdloop()

    def _validate_args(self):
        pass

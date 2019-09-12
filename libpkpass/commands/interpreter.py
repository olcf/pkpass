"""This module allows for opening a PkPass interactive interpreter"""
from __future__ import print_function
import argparse
import os
import glob
import subprocess
from cmd2 import Cmd, with_argparser
from libpkpass.commands.command import Command
from libpkpass.commands.cli import Cli
import libpkpass.commands.clip as clip
import libpkpass.commands.create as create
import libpkpass.commands.delete as delete
import libpkpass.commands.distribute as distribute
import libpkpass.commands.export as export
import libpkpass.commands.fileimport as pkimport
import libpkpass.commands.generate as generate
import libpkpass.commands.list as pklist
import libpkpass.commands.listrecipients as listrecipients
import libpkpass.commands.recover as recover
import libpkpass.commands.rename as rename
import libpkpass.commands.show as show
import libpkpass.commands.update as update

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
        Cli().cmdloop()

    def _validate_args(self):
        pass

class Interactive(Cmd, object):
    """This class implements the interactive interpreter functionality"""
    prompt = 'pkpass> '
    intro = "Welcome! Type ? to list commands"

    ####################################################################
    def __init__(self, args):
    ####################################################################
        Cmd.__init__(self)
        # Hash of registered subparser actions, mapping string to actual subparser
        self.actions = {}
        self.parser = argparse.ArgumentParser(
            description='Public Key Password Manager')

        home = os.path.expanduser("~")
        self.parser.add_argument(
            '--config', type=str, help="Path to a PKPass configuration file.  Defaults to '~/.pkpassrc'",
            default=os.path.join(home, '.pkpassrc'))
        self.subparsers = self.parser.add_subparsers(
            help='sub-commands', dest='subparser_name')

        clip.Clip(self)
        create.Create(self)
        delete.Delete(self)
        distribute.Distribute(self)
        export.Export(self)
        generate.Generate(self)
        pkimport.Import(self)
        pklist.List(self)
        listrecipients.Listrecipients(self)
        recover.Recover(self)
        rename.Rename(self)
        show.Show(self)
        update.Update(self)

        # Hold onto args passed on the command line
        self.pre_args = args
        if 'pwstore' in self.pre_args and self.pre_args['pwstore']:
            os.chdir(self.pre_args['pwstore'])

        # We basically need to grab the first argument and ditch it
        self.parser.add_argument(
            'interpreter', type=str)
        self.parsedargs = {}

    ####################################################################
    def register(self, command_obj, command_name, command_description):
        """ Register command objects and names using an observer pattern """
    ####################################################################
        self.actions[command_name] = command_obj
        parser = self.subparsers.add_parser(
            command_name, help=command_description)
        command_obj.register(parser)

    #####################################################################
    #def default(self, line):
    #####################################################################
    #    print(line)
    #    linesplit = shlex.split(line)
    #    print(linesplit)
    #    args = self.parser.parse_args(shlex.split(line))
    #    print(args)
    #    if hasattr(args, 'func'):
    #        args.func(args)
    #    else:
    #        Cmd.default(self, line)

    ####################################################################
    def _append_slash_if_dir(self, p):
    ####################################################################
        if p and os.path.isdir(p) and p[-1] != os.sep:
            return p + os.sep
        return p

    ####################################################################
    def autocomplete_file_path(self, text, line, begidx, endidx):
        """ File path autocompletion, used with the cmd module complete_* series functions"""
    ####################################################################
        # http://stackoverflow.com/questions/16826172/filename-tab-completion-in-cmd-cmd-of-python
        before_arg = line.rfind(" ", 0, begidx)
        if before_arg == -1:
            return # arg not found

        fixed = line[before_arg+1:begidx]  # fixed portion of the arg
        arg = line[before_arg+1:endidx]
        pattern = arg + '*'

        completions = []
        for path in glob.glob(pattern):
            path = self._append_slash_if_dir(path)
            completions.append(path.replace(fixed, "", 1))
        return completions

    ####################################################################
    def do_exit(self, inp):
        """Exit the application"""
    ####################################################################
        print("Bye")
        return True

    ####################################################################
    def do_edit(self, inp):
        """Edit your configuration file, with $EDITOR"""
    ####################################################################
        subprocess.call([os.environ['EDITOR'], self.pre_args['config']])

    ####################################################################
    def do_clip(self, inp):
        """Copy a password to the clipboard"""
    ####################################################################
        pkpass_command = clip.Clip(self)
        self.parsedargs = self.parser.parse_args()
        self.parsedargs.subparser_name = 'clip'
        dummy = pkpass_command.run(self.parsedargs)
        return False

    ####################################################################
    def complete_clip(self, text, line, begidx, endidx):
    ####################################################################
        return self.autocomplete_file_path(text, line, begidx, endidx)

    ####################################################################
    # @with_argparser(argparse.ArgumentParser(description='Public Key Password Manager'))
    def do_create(self, args):
        """Create a password"""
    ####################################################################
        create.Create(self)
        self.parsedargs = self.parser.parse_args()
        print(self.parsedargs)
        print(args)
        self.actions['create'].run(self.parsedargs)
        return False

    ####################################################################
    def complete_create(self, text, line, begidx, endidx):
    ####################################################################
        return self.autocomplete_file_path(text, line, begidx, endidx)

    ####################################################################
    def do_delete(self, inp):
        """Delete a password"""
    ####################################################################
        pkpass_command = delete.Delete(self)
        self.parsedargs = self.parser.parse_args()
        self.parsedargs.subparser_name = 'Delete'
        dummy = pkpass_command.run(self.parsedargs)
        return False

    ####################################################################
    def complete_delete(self, text, line, begidx, endidx):
    ####################################################################
        return self.autocomplete_file_path(text, line, begidx, endidx)

    ####################################################################
    def do_distribute(self, inp):
        """Distribute a password"""
    ####################################################################
        pkpass_command = distribute.Distribute(self)
        self.parsedargs = self.parser.parse_args()
        self.parsedargs.subparser_name = 'distribute'
        dummy = pkpass_command.run(self.parsedargs)
        return False

    ####################################################################
    def complete_distribute(self, text, line, begidx, endidx):
    ####################################################################
        return self.autocomplete_file_path(text, line, begidx, endidx)

    ####################################################################
    def do_export(self, inp):
        """Export passwords to file"""
    ####################################################################
        pkpass_command = export.Export(self)
        self.parsedargs = self.parser.parse_args()
        self.parsedargs.subparser_name = 'Export'
        dummy = pkpass_command.run(self.parsedargs)
        return False

    ####################################################################
    def do_list(self, inp):
        """List available passwords"""
    ####################################################################
        pkpass_command = pklist.List(self)
        self.parsedargs = self.parser.parse_args()
        self.parsedargs.subparser_name = 'list'
        dummy = pkpass_command.run(self.parsedargs)
        return False

    ####################################################################
    def do_listrecipients(self, inp):
        """List recipients database"""
    ####################################################################
        pkpass_command = listrecipients.Listrecipients(self)
        self.parsedargs = self.parser.parse_args()
        self.parsedargs.subparser_name = 'listrecipients'
        dummy = pkpass_command.run(self.parsedargs)
        return False

    ####################################################################
    def do_import(self, inp):
        """Create passwords from an import file"""
    ####################################################################
        pkpass_command = pkimport.Import(self)
        self.parsedargs = self.parser.parse_args()
        self.parsedargs.subparser_name = 'import'
        dummy = pkpass_command.run(self.parsedargs)
        return False

    ####################################################################
    def do_generate(self, inp):
        """Generate a password"""
    ####################################################################
        pkpass_command = generate.Generate(self)
        self.parsedargs = self.parser.parse_args()
        self.parsedargs.subparser_name = 'generate'
        dummy = pkpass_command.run(self.parsedargs)
        return False

    ####################################################################
    def complete_generate(self, text, line, begidx, endidx):
    ####################################################################
        return self.autocomplete_file_path(text, line, begidx, endidx)

    ####################################################################
    def do_recover(self, inp):
        """Recover a password"""
    ####################################################################
        pkpass_command = recover.Recover(self)
        self.parsedargs = self.parser.parse_args()
        self.parsedargs.subparser_name = 'recover'
        dummy = pkpass_command.run(self.parsedargs)
        return False

    ####################################################################
    def complete_recover(self, text, line, begidx, endidx):
    ####################################################################
        return self.autocomplete_file_path(text, line, begidx, endidx)

    ####################################################################
    def do_rename(self, inp):
        """Rename a password"""
    ####################################################################
        pkpass_command = rename.Rename(self)
        self.parsedargs = self.parser.parse_args()
        self.parsedargs.subparser_name = 'rename'
        dummy = pkpass_command.run(self.parsedargs)
        return False

    ####################################################################
    def complete_rename(self, text, line, begidx, endidx):
    ####################################################################
        return self.autocomplete_file_path(text, line, begidx, endidx)

    ####################################################################
    def do_show(self, inp):
        """Show the value of a password"""
    ####################################################################
        pkpass_command = show.Show(self)
        self.parsedargs = self.parser.parse_args()
        self.parsedargs.subparser_name = 'show'
        dummy = pkpass_command.run(self.parsedargs)
        return False

    ####################################################################
    def complete_show(self, text, line, begidx, endidx):
    ####################################################################
        return self.autocomplete_file_path(text, line, begidx, endidx)

    ####################################################################
    def do_update(self, inp):
        """Update a password value and distribute"""
    ####################################################################
        pkpass_command = update.Update(self)
        self.parsedargs = self.parser.parse_args()
        self.parsedargs.subparser_name = 'update'
        dummy = pkpass_command.run(self.parsedargs)
        return False

    ####################################################################
    def complete_update(self, text, line, begidx, endidx):
    ####################################################################
        return self.autocomplete_file_path(text, line, begidx, endidx)

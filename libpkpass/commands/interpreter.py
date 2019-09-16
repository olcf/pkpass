"""This module allows for opening a PkPass interactive interpreter"""
# Look, I know what I did; I'm sorry about the following file.
# I pray that there exists a better why to do this. This file
# Should be burned to the ground and never spoken of again.
# You know it, I know it, everybody knows it.

from __future__ import print_function
import argparse
import os
import sys
import glob
import subprocess
from cmd import Cmd
import yaml
from libpkpass.commands.command import Command
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
from libpkpass.errors import PKPassError

####################################################################
class Interpreter(Command):
    """This class implements a skeleton to call the interpreter"""
    name = 'interpreter'
    description = 'Interactive mode for pkpass'
    selected_args = ['cabundle', 'card_slot', 'certpath', 'connect', 'escrow_users', 'min_escrow',
                     'groups', 'identity', 'keypath', 'pwstore']
####################################################################

    ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                      """
    ####################################################################
        Interactive(self.args, self.identities).cmdloop()

    ####################################################################
    def _validate_args(self):
    ####################################################################
        pass

####################################################################
class Interactive(Cmd):
    """This class implements the interactive interpreter functionality"""
    intro = """Welcome to PKPass(Public Key Based Password Manager)!
Type ? to list commands"""
    prompt = 'pkpass> '
####################################################################

    ####################################################################
    def __init__(self, args, recipents_database):
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
        sys.argv.remove('interpreter')
        self._change_pwstore()

        # We basically need to grab the first argument and ditch it
        self.parsedargs = {}

    ####################################################################
    def _change_pwstore(self):
        """Change directory"""
    ####################################################################
        direc = self.pre_args['pwstore']
        if 'pwstore' in self.pre_args and direc and os.path.isdir(direc):
            os.chdir(direc)

    ####################################################################
    def _reload_config(self):
        """Change affected globals in interpreter"""
    ####################################################################
        config = self.pre_args['config']
        try:
            with open(config, 'r') as fname:
                config_args = yaml.safe_load(fname)
            if config_args is None:
                config_args = {}
        except IOError:
            print("No .pkpassrc file found, consider running ./setup.sh")
        finally:
            self.pre_args['pwstore'] = config_args['pwstore']
            self._change_pwstore()

    ####################################################################
    def register(self, command_obj, command_name, command_description):
        """ Register command objects and names using an observer pattern """
    ####################################################################
        self.actions[command_name] = command_obj
        parser = self.subparsers.add_parser(
            command_name, help=command_description)
        command_obj.register(parser)

    ####################################################################
    def precmd(self, line):
        """ Fix command line arguments, this is a hack to allow argparse
        function as we expect """
    ####################################################################
        sys.argv = [sys.argv[0]]
        sys.argv.extend(line.split())
        return line

    ####################################################################
    def postcmd(self, stop, line):
        """ Fix command line arguments, this is a hack to allow argparse
        function as we expect """
    ####################################################################
        if str(line) == "edit":
            self._reload_config()
        return Cmd.postcmd(self, stop, line)

    ####################################################################
    def _append_slash_if_dir(self, path_arg):
        """ Appending slashes for autocomplete_file_path """
    ####################################################################
        if path_arg and os.path.isdir(path_arg) and path_arg[-1] != os.sep:
            return path_arg + os.sep
        return path_arg

    ####################################################################
    def _autocomplete_file_path(self, _, line, begidx, endidx):
        """ File path autocompletion, used with the cmd module complete_* series functions"""
    ####################################################################
        before_arg = line.rfind(" ", 0, begidx)
        if before_arg == -1:
            return None # arg not found

        fixed = line[before_arg+1:begidx]  # fixed portion of the arg
        arg = line[before_arg+1:endidx]
        pattern = arg + '*'

        completions = []
        for path in glob.glob(pattern):
            path = self._append_slash_if_dir(path)
            completions.append(path.replace(fixed, "", 1))
        return completions

    ####################################################################
    def default(self, line):
        """If we don't have a proper subcommand passed"""
    ####################################################################
        print("Command '%s' not found, see help (?) for available commands"
              % line)
        return False


    ####################################################################
    def do_exit(self, _):
        """Exit the application"""
    ####################################################################
        print("Bye")
        return True

    ####################################################################
    def do_edit(self, _):
        """Edit your configuration file, with $EDITOR"""
    ####################################################################
        try:
            subprocess.call([os.environ['EDITOR'], self.pre_args['config']])
            return False
        except PKPassError as err:
            print(err)
            return False

    ####################################################################
    def do_clip(self, _):
        """Copy a password to the clipboard"""
    ####################################################################
        try:
            pkpass_command = clip.Clip(self)
            self.parsedargs = self.parser.parse_args()
            self.parsedargs.subparser_name = 'clip'
            dummy = pkpass_command.run(self.parsedargs)
            return False
        except PKPassError as err:
            print(err)
            return False

    ####################################################################
    def complete_clip(self, text, line, begidx, endidx):
    ####################################################################
        return self._autocomplete_file_path(text, line, begidx, endidx)

    ####################################################################
    def do_create(self, _):
        """Create a password"""
    ####################################################################
        try:
            create.Create(self)
            self.parsedargs = self.parser.parse_args()
            self.actions['create'].run(self.parsedargs)
            return False
        except PKPassError as err:
            print(err.msg)
            return False

    ####################################################################
    def complete_create(self, text, line, begidx, endidx):
    ####################################################################
        return self._autocomplete_file_path(text, line, begidx, endidx)

    ####################################################################
    def do_delete(self, _):
        """Delete a password"""
    ####################################################################
        try:
            delete.Delete(self)
            self.parsedargs = self.parser.parse_args()
            self.actions['delete'].run(self.parsedargs)
            return False
        except PKPassError as err:
            print(err)
            return False

    ####################################################################
    def complete_delete(self, text, line, begidx, endidx):
    ####################################################################
        return self._autocomplete_file_path(text, line, begidx, endidx)

    ####################################################################
    def do_distribute(self, _):
        """Distribute a password"""
    ####################################################################
        try:
            distribute.Distribute(self)
            self.parsedargs = self.parser.parse_args()
            self.actions['distribute'].run(self.parsedargs)
            return False
        except PKPassError as err:
            print(err)
            return False

    ####################################################################
    def complete_distribute(self, text, line, begidx, endidx):
    ####################################################################
        return self._autocomplete_file_path(text, line, begidx, endidx)

    ####################################################################
    def do_export(self, _):
        """Export passwords to file"""
    ####################################################################
        try:
            export.Export(self)
            self.parsedargs = self.parser.parse_args()
            self.actions['export'].run(self.parsedargs)
            return False
        except PKPassError as err:
            print(err)
            return False

    ####################################################################
    def do_list(self, _):
        """List available passwords"""
    ####################################################################
        try:
            pklist.List(self)
            self.parsedargs = self.parser.parse_args()
            self.actions['list'].run(self.parsedargs)
            return False
        except PKPassError as err:
            print(err)
            return False

    ####################################################################
    def do_listrecipients(self, _):
        """List recipients database"""
    ####################################################################
        try:
            listrecipients.Listrecipients(self)
            self.parsedargs = self.parser.parse_args()
            self.actions['listrecipients'].run(self.parsedargs)
            return False
        except PKPassError as err:
            print(err)
            return False

    ####################################################################
    def do_import(self, _):
        """Create passwords from an import file"""
    ####################################################################
        try:
            pkimport.Import(self)
            self.parsedargs = self.parser.parse_args()
            self.actions['import'].run(self.parsedargs)
            return False
        except PKPassError as err:
            print(err)
            return False

    ####################################################################
    def do_generate(self, _):
        """Generate a password"""
    ####################################################################
        try:
            generate.Generate(self)
            self.parsedargs = self.parser.parse_args()
            self.actions['generate'].run(self.parsedargs)
            return False
        except PKPassError as err:
            print(err)
            return False

    ####################################################################
    def complete_generate(self, text, line, begidx, endidx):
    ####################################################################
        return self._autocomplete_file_path(text, line, begidx, endidx)

    ####################################################################
    def do_recover(self, _):
        """Recover a password"""
    ####################################################################
        try:
            recover.Recover(self)
            self.parsedargs = self.parser.parse_args()
            self.actions['recover'].run(self.parsedargs)
            return False
        except PKPassError as err:
            print(err)
            return False

    ####################################################################
    def complete_recover(self, text, line, begidx, endidx):
    ####################################################################
        return self._autocomplete_file_path(text, line, begidx, endidx)

    ####################################################################
    def do_rename(self, _):
        """Rename a password"""
    ####################################################################
        try:
            rename.Rename(self)
            self.parsedargs = self.parser.parse_args()
            self.actions['rename'].run(self.parsedargs)
            return False
        except PKPassError as err:
            print(err)
            return False

    ####################################################################
    def complete_rename(self, text, line, begidx, endidx):
    ####################################################################
        return self._autocomplete_file_path(text, line, begidx, endidx)

    ####################################################################
    def do_show(self, _):
        """Show the value of a password"""
    ####################################################################
        try:
            show.Show(self)
            self.parsedargs = self.parser.parse_args()
            self.actions['show'].run(self.parsedargs)
            return False
        except PKPassError as err:
            print(err)
            return False

    ####################################################################
    def complete_show(self, text, line, begidx, endidx):
    ####################################################################
        return self._autocomplete_file_path(text, line, begidx, endidx)

    ####################################################################
    def do_update(self, _):
        """Update a password value and distribute"""
    ####################################################################
        try:
            update.Update(self)
            self.parsedargs = self.parser.parse_args()
            self.actions['update'].run(self.parsedargs)
            return False
        except PKPassError as err:
            print(err)
            return False

    ####################################################################
    def complete_update(self, text, line, begidx, endidx):
    ####################################################################
        return self._autocomplete_file_path(text, line, begidx, endidx)

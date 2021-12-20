"""This module allows for opening a PkPass interactive interpreter"""
# Look, I know what I did; I'm sorry about the following file.
# I pray that there exists a better way to do this. This file
# Should be burned to the ground and never spoken of again.
# You know it, I know it, everybody knows it.

# We need to disable unused import linting because the command classes *are* actually used...
# pylint: disable=unused-import
from os import path, environ, chdir, sep
import sys
from glob import glob
from subprocess import call
from cmd import Cmd
from inspect import getmembers, isclass
from yaml.parser import ParserError
from libpkpass import LOGGER
from libpkpass.commands.command import Command
from libpkpass.errors import PKPassError, JsonArgumentError
from libpkpass.passworddb import PasswordDB
from libpkpass.util import handle_filepath_args, show_version, collect_args
from libpkpass.commands import card, clip, create, delete, \
    distribute, export, generate, info, listrecipients, \
    modify, recover, rename, show, populate, update, pkinterface
import libpkpass.commands.fileimport as pkimport
import libpkpass.commands.list as pklist

VERSION = None
for mesg in show_version():
    VERSION = mesg

    ####################################################################
class Interpreter(Command):
    """This class implements a skeleton to call the interpreter"""
    name = 'interpreter'
    description = 'Interactive mode for pkpass'
    selected_args = Command.selected_args + ['card_slot', 'connect', 'escrow_users', 'min_escrow',
                                             'groups', 'keypath', 'pwstore']
    ####################################################################

        ####################################################################
    def _run_command_execution(self):
        """ Run function for class. """
        ####################################################################
        passworddb = PasswordDB()
        passworddb.load_from_directory(self.args['pwstore'])
        Interactive(self.args, passworddb).cmdloop_with_keyboard_interrupt()
        yield "Goodbye"

        ####################################################################
    def _validate_args(self):
        ####################################################################
        pass

# This is to keep argparse from sys.exiting all over the place
    ####################################################################
def pkparse_error(message):
    ####################################################################
    raise PKPassError(message)

    ####################################################################
class Interactive(Cmd, pkinterface.PkInterface):
    """This class implements the interactive interpreter functionality"""
    intro = f"""Welcome to PKPass (Public Key Based Password Manager) v{VERSION}!
Type ? to list commands"""
    prompt = 'pkpass> '
    ####################################################################

        ####################################################################
    def __init__(self, args, pwdb):
        ####################################################################
        Cmd.__init__(self)
        # manually remove interpreter from command line so that argparse doesn't try to use it
        # This needs to be removed before the PkInterace init
        sys.argv.remove('interpreter')

        pkinterface.PkInterface.__init__(self)

        self.pwdb = pwdb if pwdb else PasswordDB()
        self.parser.error = pkparse_error

        # Hold onto args passed on the command line
        self.args = args
        # change our cwd so users can tab complete
        self._change_pwstore()

        # We basically need to grab the first argument and ditch it
        self.parsedargs = {}

        ####################################################################
    def cmdloop_with_keyboard_interrupt(self):
        """handle keyboard interrupts"""
        ####################################################################
        breaker = False
        first = True
        while breaker is not True:
            try:
                if first:
                    self.cmdloop()
                else:
                    self.cmdloop(intro='')
                breaker = True
            except KeyboardInterrupt:
                first = False
                sys.stdout.write('\n')

        ####################################################################
    def _load_pwdb(self):
        """reload passworddb"""
        ####################################################################
        LOGGER.info("Reloading Password Database")
        self.pwdb = PasswordDB()
        self.pwdb.load_from_directory(self.args['pwstore'])

        ####################################################################
    def _change_pwstore(self):
        """Change directory"""
        ####################################################################
        direc = self.args['pwstore']
        if 'pwstore' in self.args and direc and path.isdir(direc):
            chdir(direc)

        ####################################################################
    def _reload_config(self):
        """Change affected globals in interpreter"""
        ####################################################################
        # We still need to be able to reload other things like recipients
        # database
        config = self.args['config']
        config_args = self.args
        try:
            config_args = collect_args({'config': config})
            if not config_args:
                config_args = self.args
        except ParserError:
            LOGGER.error("Error parsing config file")
            config_args = self.args
        finally:
            self.args = config_args
            self.args['config'] = config
            self.args = handle_filepath_args(self.args)
            self._change_pwstore()
            self._load_pwdb()

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
        if str(line) == "edit" or '--no-cache' in line:
            self._reload_config()
        elif str(line.split()[0]) in ['create', 'delete', 'import', 'generate', 'rename']:
            self._load_pwdb()
        return Cmd.postcmd(self, stop, line)

        ####################################################################
    def _append_slash_if_dir(self, path_arg):
        """ Appending slashes for autocomplete_file_path """
        ####################################################################
        if path_arg and path.isdir(path_arg) and path_arg[-1] != sep:
            return path_arg + sep
        return path_arg

        ####################################################################
    def autocomplete_file_path(self, _, line, begidx, endidx):
        """ File path autocompletion, used with the cmd module complete_* series functions"""
        ####################################################################
        before_arg = line.rfind(" ", 0, begidx)
        if before_arg == -1:
            return None # arg not found

        fixed = line[before_arg+1:begidx]  # fixed portion of the arg
        arg = line[before_arg+1:endidx]
        pattern = arg + '*'

        completions = []
        for fpath in glob(pattern):
            fpath = self._append_slash_if_dir(fpath)
            completions.append(fpath.replace(fixed, "", 1))
        return completions

        ####################################################################
    def default(self, line):
        """If we don't have a proper subcommand passed"""
        ####################################################################
        LOGGER.error(
            "Command '%s' not found, see help (?) for available commands",
            line
        )
        return False

        ####################################################################
    def do_exit(self, _):
        """Exit the application"""
        ####################################################################
        return True

        ####################################################################
    def do_version(self, _):
        """Print the version of PkPass"""
        ####################################################################
        print(VERSION)

        ####################################################################
    def do_edit(self, _):
        """Edit your configuration file, with $EDITOR"""
        ####################################################################
        try:
            call([environ['EDITOR'], self.args['config']])
            return False
        except (IOError, SystemExit):
            return False

        ####################################################################
    def do_git(self, line):
        """If your password store is git back, you can control git from here"""
        ####################################################################
        call(["git"] + line.split())
        return False

    ##############################################################################
def add_dynamic_function(module_name, class_name):
    """This allows repetitive do_* and complete_* functions to be condensed"""
    ##############################################################################
    swap_name = module_name
    if "pk" in module_name:
        swap_name = module_name[2:]
    fn_name = "do_" + swap_name
    complete_name = "complete_" + swap_name

        ############################################
    def do_fn(self, _):
        """Use -h or --help for information"""
        ############################################
        try:
            pk_class = [o for o in getmembers(globals()[module_name], isclass)
                        if str(o[0]) == class_name][0][1]
            pk_class(self, pwdb=self.pwdb)
            for mesg in self.actions[swap_name].run(self.parser.parse_args()):
                if mesg:
                    print(mesg)
            return False
        except PKPassError as err:
            LOGGER.error(err)
            return False
        except SystemExit:
            return False

        ##################################################
    def complete_fn(self, text, line, begidx, endidx):
        ##################################################
        return self.autocomplete_file_path(text, line, begidx, endidx)

    setattr(Interactive, fn_name, do_fn)
    setattr(Interactive, complete_name, complete_fn)

for command in [('card', 'Card'), ('clip', 'Clip'), ('create', 'Create'), ('delete', 'Delete'),
                ('distribute', 'Distribute'), ('export', 'Export'),
                ('generate', 'Generate'), ('pkimport', 'Import'), ('info', 'Info'),
                ('pklist', 'List'), ('listrecipients', 'Listrecipients'),
                ('modify', 'Modify'), ('recover', 'Recover'), ('rename', 'Rename'),
                ('show', 'Show'), ('populate', 'Populate'), ('update', 'Update')]:
    add_dynamic_function(command[0], command[1])

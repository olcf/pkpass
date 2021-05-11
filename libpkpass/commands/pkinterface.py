#!/usr/bin/env python3
"""This is a super class to handle commonalities between the cli and interpreter"""
from argparse import ArgumentParser
from os import path
import libpkpass.util as util
import libpkpass.commands.card as card
import libpkpass.commands.clip as clip
import libpkpass.commands.create as create
import libpkpass.commands.delete as delete
import libpkpass.commands.distribute as distribute
import libpkpass.commands.export as export
import libpkpass.commands.fileimport as pkimport
import libpkpass.commands.generate as generate
import libpkpass.commands.info as info
import libpkpass.commands.list as pklist
import libpkpass.commands.listrecipients as listrecipients
import libpkpass.commands.modify as modify
import libpkpass.commands.recover as recover
import libpkpass.commands.rename as rename
import libpkpass.commands.show as show
import libpkpass.commands.populate as populate
import libpkpass.commands.update as update
import libpkpass.commands.verifyinstall as verifyinstall

    ##############################################################################
class PkInterface():
    """ Class for parsing command line.  Observes subclasses of Command to Register
    those commands in the actions list.                                        """
    ##############################################################################
        ####################################################################
    def __init__(self):
        """ Intialization function for class. Register all subcommands   """
        ####################################################################
        # Hash of registered subparser actions, mapping string to actual subparser
        self.actions = {}
        home = path.expanduser("~")
        for file in ['.pkpassrc', '.pkpassrc.yml', '.pkpassrc.yaml']:
            if path.isfile(path.join(home, file)):
                default = path.join(home, file)
        self.parser = ArgumentParser(
            description='Public Key Password Manager')
        self.parser.set_default_subparser = util.set_default_subparser
        self.parser.add_argument(
            '--config', type=str,
            help="Path to a PKPass configuration file.  Defaults to '~/.pkpassrc{,.yml,.yaml}'",
            default=default
        )
        self.parser.add_argument('--debug', action='store_true',
                                 help="Errors are more verbose")
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
        info.Info(self)
        pklist.List(self)
        listrecipients.Listrecipients(self)
        modify.Modify(self)
        recover.Recover(self)
        rename.Rename(self)
        show.Show(self)
        populate.Populate(self)
        update.Update(self)
        verifyinstall.VerifyInstall(self)

        ####################################################################
    def register(self, command_obj, command_name, command_description):
        """ Register command objects and names using an observer pattern """
        ####################################################################
        self.actions[command_name] = command_obj
        parser = self.subparsers.add_parser(
            command_name, help=command_description)
        command_obj.register(parser)

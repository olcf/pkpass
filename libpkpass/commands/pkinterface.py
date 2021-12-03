#!/usr/bin/env python3
"""This is a super class to handle commonalities between the cli and interpreter"""
from argparse import ArgumentParser
from os import path
from libpkpass.util import set_default_subparser
from libpkpass.commands import card, clip, create, delete, \
    distribute, export, generate, info, listrecipients, \
    modify, recover, rename, show, populate, update, verifyinstall
import libpkpass.commands.fileimport as pkimport
import libpkpass.commands.list as pklist

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
        defaultrc = None
        for file in ['.pkpassrc', '.pkpassrc.yml', '.pkpassrc.yaml']:
            if path.isfile(path.join(home, file)):
                defaultrc = path.join(home, file)
        if not defaultrc:
            defaultrc = path.join(home, '.pkpassrc')
        self.parser = ArgumentParser(
            description='Public Key Password Manager')
        self.parser.set_default_subparser = set_default_subparser
        self.parser.add_argument(
            '--config', type=str,
            help="Path to a PKPass configuration file.  Defaults to '~/.pkpassrc{,.yml,.yaml}'",
            default=defaultrc
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

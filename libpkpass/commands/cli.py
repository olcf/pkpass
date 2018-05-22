#!/usr/bin/env python

import argparse
import create, distribute, show, clip, list, listrecipients, export

class Cli(object):
  ##############################################################################
  """ Class for parsing command line.  Observes subclasses of Command to Register
  those commands in the actions list.                                        """
  ##############################################################################


  def __init__(self):
    ####################################################################
    """ Intialization function for class. Register all subcommands   """
    ####################################################################
    # Hash of registered subparser actions, mapping string to actual subparser
    self.actions = {}
    self.parser = argparse.ArgumentParser(description='Public Key Password Manager')
    self.parser.add_argument('--config', type=str, help="Path to a PKPass configuration file.  Defaults to '.pkpassrc'", default='.pkpassrc' )
    self.subparsers = self.parser.add_subparsers(help='sub-commands', dest='subparser_name')

    create.Create(self)
    distribute.Distribute(self)
    show.Show(self)
    clip.Clip(self)
    list.List(self)
    listrecipients.Listrecipients(self)
    export.Export(self)


    self.parsedargs = self.parser.parse_args()
    self.actions[self.parsedargs.subparser_name].run(self.parsedargs)


  def register(self, command_obj, command_name, command_description):
    ####################################################################
    """ Register command objects and names using an observer pattern """
    ####################################################################
    self.actions[command_name] = command_obj
    parser = self.subparsers.add_parser(command_name, help=command_description)
    command_obj.register(parser)

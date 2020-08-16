"""This module allows for the automated generation of passwords"""
import re
import exrex
from libpkpass.commands.command import Command
from libpkpass.errors import CliArgumentError, NotThePasswordOwnerError, RulesMapError
from libpkpass.util import parse_json_arguments

    ####################################################################
class Generate(Command):
    """This class implements the CLI functionality of automatic generation of passwords"""
    ####################################################################
    name = 'generate'
    description = 'Generate a new password entry and encrypt it for yourself'
    selected_args = Command.selected_args + ['pwname', 'pwstore', 'overwrite', 'stdin', 'keypath',
                                             'nopassphrase', 'nosign', 'card_slot', 'escrow_users',
                                             'min_escrow', 'noescrow', 'rules', 'rules_map', 'description',
                                             'authorizer']

        ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                      """
        ####################################################################
        safe, owner = self.safety_check()
        if not self.args['description']:
            self.args['description'] = input("Description: ")

        if not self.args['authorizer']:
            self.args['authorizer'] = input("Authorizer: ")

        if safe or self.args['overwrite']:
            password = self._generate_pass()

            self.create_or_update_pass(password, self.argsp['description'], self.args['authorizer'])
        else:
            raise NotThePasswordOwnerError(self.args['identity'], owner, self.args['pwname'])

        ####################################################################
    def _generate_pass(self):
        """ Generate a password based on a rules list that has been provided"""
        #######################################################################
        try:
            regex_rule = self.args['rules_map'][self.args['rules']]
            password = exrex.getone(regex_rule)
            # The following regex search verifies it finds a match from exrex
            return re.search(regex_rule, password).group(0)
        except TypeError:
            raise RulesMapError("Poorly formatted Rules Map, please check it is in json format")
        except re.error:
            raise RulesMapError("Poorly formatted regex, or unsupported")

        #######################################################################
    def _validate_args(self):
        #######################################################################
        self.args['rules_map'] = parse_json_arguments(self.args, 'rules_map')
        for argument in ['pwname', 'keypath', 'rules_map']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)
        if self.args['rules'] not in self.args['rules_map'] or self.args['rules_map'][self.args['rules']] == "":
            raise RulesMapError("No Rule set defined as %s" % self.args['rules'])

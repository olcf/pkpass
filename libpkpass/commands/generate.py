"""This module allows for the automated generation of passwords"""
from __future__ import print_function
import random
from os import urandom
from builtins import input
from libpkpass.commands.command import Command
from libpkpass.errors import CliArgumentError, NotThePasswordOwnerError, RulesMapError

class Generate(Command):
    """This class implements the CLI functionality of automatic generation of passwords"""
    name = 'generate'
    description = 'Generate a new password entry and encrypt it for yourself'
    selected_args = ['pwname', 'pwstore', 'overwrite', 'stdin', 'identity', 'certpath',
                     'keypath', 'cabundle', 'nopassphrase', 'noverify', 'nosign', 'card_slot',
                     'escrow_users', 'min_escrow', 'noescrow', 'rules', 'rules_map']
    char_set = {
        'lower': 'abcdefghijklmnopqrstuvwxyz',
        'upper': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'numbers': '0123456789',
        'special': r'^!\$%&/()=?{[]}+~#-_.:,;<>|\\'
    }

    def _run_command_execution(self):
        ####################################################################
        """ Run function for class.                                      """
        ####################################################################
        safe, owner = self.safety_check()
        if safe or self.args['overwrite']:
            password = self._generate_pass()

            description = input("Description: ")
            authorizer = input("Authorizer: ")
            self.create_pass(password, description, authorizer)
        else:
            raise NotThePasswordOwnerError(self.args['identity'], owner)

    def _generate_pass(self):
        #######################################################################
        """ Generate a password based on a rules list that has been provided"""
        #######################################################################
        try:
            rules_list = self.args['rules_map'][self.args['rules']]
            local_set = {}
            if 'length' not in rules_list:
                rules_list['length'] = 12
            rules_list['length'] = int(rules_list['length'])
            for key, value in rules_list.items():
                if not isinstance(value, int) and value.encode("ASCII").upper() == "TRUE":
                    as_key = key.encode("ASCII")
                    local_set[as_key] = self.char_set[as_key]
            password = []
            while True:
                while len(password) < rules_list['length']:
                    key = random.choice(local_set.keys())
                    a_char = urandom(1)
                    if a_char in local_set[key]:
                        if self.check_prev_char(password, local_set[key]):
                            continue
                        else:
                            password.append(a_char)
                if self._rules_check(local_set, ''.join(password)):
                    break
            return ''.join(password)
        except TypeError:
            raise RulesMapError("Poorly formatted Rules Map, please check it is in json format")
        except KeyError as err:
            raise RulesMapError("No supported rule fitting name %s" % err)

    def check_prev_char(self, password, current_char_set):
        #######################################################################
        """Function to ensure no consecutive chars"""
        #######################################################################
        index = len(password)
        if index == 0:
            return False
        prev_char = password[index - 1]
        if prev_char in current_char_set:
            return True
        return False

    def _rules_check(self, rules_list, attempt):
        ##############################################################
        """ Validate that the rules for the password has been met  """
        ##############################################################
        rules_dict = {
            "upper": lambda s: any(x.isupper() for x in s), # must have at least one uppercase
            "lower": lambda s: any(x.islower() for x in s),  # must have at least one lowercase
            "digits": lambda s: any(x.isdigit() for x in s),  # must have at least one digit
            "length": lambda s: len(s) >= rules_list['length'] # Character length
        }
        for key, value in rules_dict.items():
            if key in rules_list.keys():
                if not value(attempt):
                    return False
        return True

    def _validate_args(self):
        for argument in ['pwname', 'keypath', 'rules_map']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)
        if self.args['rules'] not in self.args['rules_map']:
            raise RulesMapError("No Rule set defind as %s" % self.args['rules'])

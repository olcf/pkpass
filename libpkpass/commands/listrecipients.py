"""This Module allows for the listing of recipients"""

from __future__ import print_function
from libpkpass.commands.command import Command
from libpkpass.errors import CliArgumentError


class Listrecipients(Command):
    """This class implements the cli functionality to list recipients"""
    name = 'listrecipients'
    description = 'List the recipients that pkpass knows about'
    selected_args = Command.selected_args + ['stdin', 'filter']

    ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                  """
    ####################################################################

        if self.args['verbosity'] != -1:
            print('Certificate store: "%s"' % self.args['certpath'])
            print('Key store: "%s"' % self.args['keypath'])
            print('CA Bundle file: "%s"' % self.args['cabundle'])
            print('Looking for Key Extension: "%s"' %
                  self.identities.extensions['key'])
            print('Looking for Certificate Extension: "%s"' %
                  self.identities.extensions['certificate'])

            print("Loaded %s identities:\n" % len(self.identities.iddb.keys()))

        # we don't want to overwrite iddb because of the interpreter
        if 'filter' in self.args and self.args['filter']:
            tempiddb = {k:v for k, v in self.identities.iddb.items() if self.args['filter'] in k}
        else:
            tempiddb = self.identities.iddb
        for key, _ in tempiddb.items():
            self._print_identity(key)

    ####################################################################
    def _print_identity(self, key):
        """Print off identity"""
    ####################################################################
        print("%s:\n\tVerified: %s\n\tSubject: %s\n\tSubject Hash: %s\n\tIssuer: %s\n\tIssuer Hash: %s\n\tFingerprint: %s\n\tExpires: %s\n" % (
            self.identities.iddb[key]['uid'],
            self.identities.iddb[key]['verified'],
            self.identities.iddb[key]['subject'],
            self.identities.iddb[key]['subjecthash'],
            self.identities.iddb[key]['issuer'],
            self.identities.iddb[key]['issuerhash'],
            self.identities.iddb[key]['fingerprint'],
            self.identities.iddb[key]['enddate']))

    ####################################################################
    def _validate_args(self):
        """ Ensure arguments are appropriate for this command       """
    ####################################################################
        for argument in ['keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument)

    ####################################################################
    def _validate_identities(self):
        """ Ensure identities are appropriate for this command       """
    ####################################################################
        return

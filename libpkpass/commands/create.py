import getpass
import os
from command import Command
from libpkpass.identities import IdentityDB
from libpkpass.password import PasswordEntry
from libpkpass.errors import *

class Create(Command):
  name='create'
  description='Create a new password entry and encrypt it for yourself'
  selected_args = ['pwname', 'pwstore', 'overwrite', 'stdin', 'identity', 'certpath', 'keypath', 'cabundle', 'nopassphrase', 'noverify', 'nosign']


  def _run_command_execution(self):
    ####################################################################
    """ Run function for class.                                      """
    ####################################################################
    password1 = getpass.getpass("Enter password to create: ")
    password2 = getpass.getpass("Enter password to create again: ")
    if password1 != password2: raise PasswordMismatchError

    password_metadata = {}
    for item in ['Name', 'Description', 'Authorizer']:
      password_metadata[item.lower()] = raw_input("%s: " % item)
    password_metadata['creator'] = self.args['identity']

    password = PasswordEntry(**password_metadata)

    password.add_recipients( secret = password1,
                             distributor = self.args['identity'],
                             recipients = [self.args['identity']],
                             identitydb = self.identities,
                             passphrase = self.passphrase
                           )

    password.write_password_data(os.path.join(self.args['pwstore'], self.args['pwname']), overwrite=self.args['overwrite'])


  def _validate_args(self):
    for argument in ['certpath', 'keypath']:
      if argument not in self.args or self.args[argument] is None:
        raise CliArgumentError("'%s' is a required argument" % argument)

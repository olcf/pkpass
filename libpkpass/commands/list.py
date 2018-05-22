import os
import yaml
from command import Command
from libpkpass.identities import IdentityDB
from libpkpass.passworddb import PasswordDB
from libpkpass.errors import *

class List(Command):
  name='list'
  description='List passwords you have access to'
  selected_args = ['pwstore', 'stdin', 'identity', 'certpath', 'cabundle', 'noverify']


  def _run_command_execution(self):
    ####################################################################
    """ Run function for class.                                      """
    ####################################################################

    passworddb = PasswordDB()
    for path, dirs, files in os.walk( self.args['pwstore'] ):
      for passwordname in files:
        passwordpath = os.path.join( path, passwordname )
        passworddb.load_password_data( passwordpath )

    result = {}
    for pwname, passwordentry in passworddb.pwdb.items():
      if( self.args['identity'] in passwordentry.recipients.keys() ):
        result[pwname] = { 'name': passwordentry.metadata['name'],
                           'distributor': passwordentry.recipients[self.args['identity']]['distributor']
                         }

    print("Passwords for '%s':" % self.args['identity'])
    print("\n%s" % yaml.dump(result, default_flow_style=False))


  def _validate_args(self):
    for argument in ['certpath', 'keypath']:
      if argument not in self.args or self.args[argument] is None:
        raise CliArgumentError("'%s' is a required argument" % argument)

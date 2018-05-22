import os
from command import Command
from libpkpass.identities import IdentityDB
from libpkpass.password import PasswordEntry
from libpkpass.errors import *

class Show(Command):
  name='show'
  description='Display a password'
  selected_args = ['pwname', 'pwstore', 'stdin', 'identity', 'certpath', 'keypath', 'cabundle', 'nopassphrase', 'noverify']


  def _run_command_execution(self):
    ####################################################################
    """ Run function for class.                                      """
    ####################################################################

    password = PasswordEntry()
    password.read_password_data(os.path.join(self.args['pwstore'], self.args['pwname']))
    myidentity = self.identities.iddb[self.args['identity']]

    plaintext_pw = password.decrypt_entry(
            identity = myidentity,
            passphrase = self.passphrase )

    if( not self.args['noverify'] ):
      result = password.verify_entry( myidentity['uid'], self.identities.iddb )
      if not result['sigOK']:
        print("Warning:  Could not verify that '%s' correctly signed your password entry." % result['distributor'])
      if not result['certOK']:
        print("Warning:  Could not verify the certificate authenticity of user '%s'." % result['distributor'])

    print("%s: %s") % (password.metadata['name'], plaintext_pw)


  def _validate_args(self):
    for argument in ['certpath', 'keypath']:
      if argument not in self.args or self.args[argument] is None:
        raise CliArgumentError("'%s' is a required argument" % argument)

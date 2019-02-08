"""This Module defines what a passworddb should look like"""
import os
import yaml
from libpkpass.password import PasswordEntry
from libpkpass.errors import PasswordIOError


class PasswordDB(object):
    ##############################################################################
    """ Password database object.  Gets and retrieves password entries from places
        passwords are stored                                                   """
    ##############################################################################

    def __init__(self, mode='Filesystem'):
        self.mode = mode
        self.pwdb = {}

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __str__(self):
        return "%r" % self.__dict__

    def __sizeof__(self):
        return len(self.pwdb)

    ##############################################################################
    def load_password_data(self, password_id):
        """ Load and return password from wherever it may be stored              """
    ##############################################################################
        if not password_id in self.pwdb.keys():
            if self.mode == 'Filesystem':
                self.pwdb[password_id] = self.read_password_data_from_file(
                    password_id)
        return self.pwdb[password_id]

    ##############################################################################
    def save_password_data(self, password_id, overwrite=False):
        """ Store a password to wherever it may be stored                        """
    ##############################################################################
        if self.mode == 'Filesystem':
            self.write_password_data_to_file(
                self.pwdb[password_id], password_id, overwrite)

    ##############################################################################
    def read_password_data_from_file(self, filename):
        """ Open a password file, load passwords and read metadata               """
    ##############################################################################
        with open(filename, 'r') as fname:
            password_data = yaml.safe_load(fname)
            password_entry = PasswordEntry()
            password_entry.metadata = password_data['metadata']
            password_entry.recipients = password_data['recipients']
        password_entry.validate()
        return password_entry

    #############################################################################
    def write_password_data_to_file(self, password_data, filename, overwrite=False):
        """ Write password data and metadata to the appropriate password file """
    ##############################################################################
        try:
            if not os.path.isdir(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))
            with open(filename, 'w+') as fname:
                fname.write(yaml.dump(password_data.todict(),
                                      default_flow_style=False))
        except (OSError, IOError):
            raise PasswordIOError("Error creating '%s'" % filename)

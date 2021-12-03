"""This Module defines what a passworddb should look like"""
from os import walk, path, makedirs
from multiprocessing import Manager, cpu_count, Pool
from fnmatch import fnmatch
from yaml import safe_load, dump
from libpkpass.password import PasswordEntry
from libpkpass.errors import PasswordIOError

    ##############################################################################
class PasswordDB():
    """ Password database object.  Gets and retrieves password entries from places
        passwords are stored"""
    ##############################################################################

    def __init__(self, mode='Filesystem'):
        self.mode = mode
        self.pwdb = {}
        self.ignore = '*requirements.txt'

    def __repr__(self):
        return f"{self.__class__}({self.__dict__})"

    def __str__(self):
        return f"{self.__dict__}"

    def __sizeof__(self):
        return len(self.pwdb)

    ##############################################################################
    def load_password_data(self, password_id, pwdb=None):
        """ Load and return password from wherever it may be stored"""
    ##############################################################################
        if fnmatch(password_id, self.ignore):
            return None
        if password_id not in self.pwdb.keys() and self.mode == 'Filesystem':
            self.pwdb[password_id] = self.read_password_data_from_file(password_id)
        if pwdb is not None:
            pwdb[password_id] = self.pwdb[password_id]
        return self.pwdb[password_id]

    #############################################################################
    def load_from_directory(self, pwstore):
        """ Load all passwords from directory """
    #############################################################################
        with Manager() as manager:
            pool = Pool(cpu_count())
            pwdb = manager.dict()
            for fpath, _, files in walk(pwstore):
                pool.apply_async(self.parallel_loader, args=(files, fpath, pwdb))
            pool.close()
            pool.join()
            self.pwdb = dict(pwdb)

    ##############################################################################
    def parallel_loader(self, files, fpath, pwdb):
        """Function to allow multiprocessing to be utilize to read passwords"""
    ##############################################################################
        for passwordname in files:
            passwordpath = path.join(fpath, passwordname)
            self.load_password_data(passwordpath, pwdb)

    ##############################################################################
    def save_password_data(self, password_id, overwrite=False):
        """ Store a password to wherever it may be stored """
    ##############################################################################
        if self.mode == 'Filesystem':
            self.write_password_data_to_file(
                self.pwdb[password_id], password_id, overwrite
            )

    ##############################################################################
    def read_password_data_from_file(self, filename):
        """ Open a password file, load passwords and read metadata """
    ##############################################################################
        try:
            with open(filename, 'r', encoding='ASCII') as fname:
                password_data = safe_load(fname)
                password_entry = PasswordEntry()
                password_entry.metadata = password_data['metadata']
                password_entry.recipients = password_data['recipients']
                if 'escrow' in password_data:
                    password_entry.escrow = password_data['escrow']
            password_entry.validate()
            return password_entry
        except (OSError, IOError, TypeError) as err:
            raise PasswordIOError(
                f"Error reading '{filename}' perhaps a path error for the db, or malformed file"
            ) from err

    #############################################################################
    def write_password_data_to_file(self, password_data, filename, overwrite=False):
        """ Write password data and metadata to the appropriate password file """
    ##############################################################################
        try:
            if not path.isdir(path.dirname(filename)):
                makedirs(path.dirname(filename))
            with open(filename, 'w+', encoding='ASCII') as fname:
                passdata = {key: value for key, value in password_data.todict().items() if value}
                fname.write(dump(passdata,
                                 default_flow_style=False))
        except (OSError, IOError) as err:
            raise PasswordIOError(f"Error creating '{filename}'") from err

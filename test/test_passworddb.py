#!/usr/bin/env python

import unittest
from libpkpass.passworddb import PasswordDB
from libpkpass.password import PasswordEntry
from libpkpass.identities import IdentityDB

class TestBasicFunction(unittest.TestCase):
  def setUp(self):
    self.file1 = 'test/passwords/testpassword'
    self.file2 = 'test/scratch/testpassword'


  def test_read_write(self):
    passworddb = PasswordDB()
    passwordentry = passworddb.load_password_data( self.file1 )
    passworddb.pwdb[self.file2] = passworddb.pwdb[self.file1]
    passworddb.save_password_data(self.file2, overwrite=True )

    with open( self.file1, 'r' ) as file1:
      with open( self.file2, 'r' ) as file2:
        self.assertTrue( file1.read() == file2.read() )

if __name__ == '__main__':
  unittest.main()

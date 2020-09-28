#!/usr/bin/env python3
"""This Module tests the passworddb module"""
import unittest
from libpkpass.passworddb import PasswordDB

class TestBasicFunction(unittest.TestCase):
    """This class tests the passworddb class"""
    def setUp(self):
        self.file1 = 'test/passwords/testpassword'
        self.file2 = 'test/scratch/testpassword'

    def test_read_write(self):
        """Test read write to the password db"""
        passworddb = PasswordDB()
        passwordentry = passworddb.load_password_data(self.file1)
        passworddb.pwdb[self.file2] = passworddb.pwdb[self.file1]
        passworddb.save_password_data(self.file2, overwrite=True)

        with open(self.file1, 'r') as file1:
            with open(self.file2, 'r') as file2:
                self.assertTrue(file1.read() == file2.read())


if __name__ == '__main__':
    unittest.main()

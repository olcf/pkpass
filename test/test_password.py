#!/usr/bin/env python3
"""This Module tests the password entry module"""
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from libpkpass.password import PasswordEntry
from libpkpass.identities import IdentityDB

class TestBasicFunction(unittest.TestCase):
    """This Class tests the password entry class"""
    def setUp(self):
        self.certdir = 'test/pki/intermediate/certs'
        self.keydir = 'test/pki/intermediate/private'
        self.cabundle = 'test/pki/intermediate/certs/ca-bundle'
        self.file1 = 'test/passwords/testpassword'
        self.file2 = 'test/scratch/testpassword'
        self.secret = 'Secret'
        self.textblob = 'Testing TextField'
        self.sender = 'r1'

        self.idobj = IdentityDB()
        self.idobj.identity = self.sender
        self.idobj.recipient_list = ['r2', 'r3']
        db_path = 'test/pki/intermediate/certs/rd.db'
        self.idobj.args = {
            'db': {
                'uri': f"sqlite+pysqlite:///{db_path}",
                'engine': create_engine(f"sqlite+pysqlite:///{db_path}")
            }
        }
        self.session = sessionmaker(bind=self.idobj.args['db']['engine'])()
        self.idobj.load_certs_from_directory(self.certdir, self.cabundle)
        self.idobj.load_keys_from_directory(self.keydir)

    def test_create_encrypt_decrypt(self):
        """create a password entry"""
        passwordentry = PasswordEntry(name='testcreate',
                                      description=self.textblob,
                                      creator='r1',
                                      authorizer='r1')

        passwordentry.add_recipients(secret=self.secret,
                                     distributor='r1',
                                     recipients=self.idobj.recipient_list,
                                     session=self.session)

    def test_read_write(self):
        """Read and write password entry data"""
        passwordentry = PasswordEntry()
        passwordentry.read_password_data(self.file1)
        passwordentry.write_password_data(self.file2, overwrite=True)

        with open(self.file1, 'r', encoding='ASCII') as file1:
            with open(self.file2, 'r', encoding='ASCII') as file2:
                self.assertTrue(file1.read() == file2.read())

if __name__ == '__main__':
    unittest.main()

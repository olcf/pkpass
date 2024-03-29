#!/usr/bin/env python3
"""This Module tests iddb module"""
import unittest
import os.path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from libpkpass.identities import IdentityDB
from libpkpass.models.recipient import Recipient


class TestBasicFunction(unittest.TestCase):
    """This class tests the iddb class"""

    def setUp(self):
        self.certdir = "test/pki/intermediate/certs"
        self.keydir = "test/pki/intermediate/private"
        self.cabundle = "test/pki/intermediate/certs/ca-bundle"
        db_path = "test/pki/intermediate/certs/rd.db"
        self.iddb = IdentityDB()
        self.iddb.args = {
            "db": {
                "uri": f"sqlite+pysqlite:///{db_path}",
                "engine": create_engine(f"sqlite+pysqlite:///{db_path}"),
            }
        }
        self.iddb.session = sessionmaker(bind=self.iddb.args["db"]["engine"])()

    def test_certificate_loading(self):
        """Load a cert into our test"""
        self.iddb.load_certs_from_directory(self.certdir, self.cabundle)
        for identity in ("r1", "r2", "r3"):
            assert identity in [
                x[0] for x in self.iddb.session.query(Recipient.name).all()
            ]

    def test_key_loading(self):
        """Load a key into our test"""
        self.iddb.load_keys_from_directory(self.keydir)
        for identity in ("r1", "r2", "r3"):
            assert identity in [
                x[0] for x in self.iddb.session.query(Recipient.name).all()
            ]
            test_id = (
                self.iddb.session.query(Recipient)
                .filter(Recipient.name == identity)
                .first()
            )
            assert os.path.isfile(test_id.key)

    def test_keycert_loading(self):
        """Load a keycert into our test"""
        self.iddb.load_certs_from_directory(self.certdir, self.cabundle)
        self.iddb.load_keys_from_directory(self.keydir)
        for identity in ("r1", "r2", "r3"):
            assert identity in [
                x[0] for x in self.iddb.session.query(Recipient.name).all()
            ]
            test_id = (
                self.iddb.session.query(Recipient)
                .filter(Recipient.name == identity)
                .first()
            )
            assert os.path.isfile(test_id.key)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python

import unittest
import os.path
from libpkpass.identities import IdentityDB

class TestBasicFunction(unittest.TestCase):
  def setUp(self):
    self.certdir = 'test/pki/intermediate/certs'
    self.keydir = 'test/pki/intermediate/private'
    self.cabundle = 'test/pki/intermediate/certs/ca-bundle'


  def test_certificate_loading(self):
    idobj = IdentityDB()
    idobj.load_certs_from_directory(self.certdir, self.cabundle)
    for identity in ('r1', 'r2', 'r3'):
      assert identity in idobj.iddb
      assert idobj.iddb[identity]['uid'] == identity
      assert os.path.isfile( idobj.iddb[identity]['certificate_path'] )

  def test_key_loading(self):
    idobj = IdentityDB()
    idobj.load_keys_from_directory(self.keydir)
    for identity in ('r1', 'r2', 'r3'):
      assert identity in idobj.iddb
      assert idobj.iddb[identity]['uid'] == identity
      assert os.path.isfile( idobj.iddb[identity]['key_path'] )

  def test_keycert_loading(self):
    idobj = IdentityDB()
    idobj.load_certs_from_directory(self.certdir, self.cabundle)
    idobj.load_keys_from_directory(self.keydir)
    for identity in ('r1', 'r2', 'r3'):
      assert identity in idobj.iddb
      assert idobj.iddb[identity]['uid'] == identity
      assert os.path.isfile( idobj.iddb[identity]['certificate_path'] )
      assert os.path.isfile( idobj.iddb[identity]['key_path'] )


if __name__ == '__main__':
  unittest.main()

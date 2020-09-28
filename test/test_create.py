#!/usr/bin/env python3
"""This module tests the create module"""
import getpass
import builtins
import unittest
import mock
import libpkpass.commands.cli as cli
import libpkpass.commands.create as create
from libpkpass.errors import CliArgumentError, DecryptionError
from .basetest.basetest import patch_args, ERROR_MSGS

class CreateTests(unittest.TestCase):
    """This class tests the create class"""
    def test_create_success(self):
        """Test a success creation of a password"""
        ret = True
        try:
            with patch_args(subparser_name='create', identity='r1', nopassphrase='true',
                            pwname='test'):
                with mock.patch.object(builtins, 'input', lambda _: 'y'):
                    with mock.patch.object(getpass, 'getpass', lambda _: 'y'):
                        create.Create(cli.Cli())
        except DecryptionError:
            ret = False
        self.assertTrue(ret)

    def test_create_no_pass(self):
        """Test what happens with pwname is not supplied"""
        with self.assertRaises(CliArgumentError) as context:
            with patch_args(subparser_name='create', identity='r1', nopassphrase='true',
                            pwname=None):
                with mock.patch.object(builtins, 'input', lambda _: 'y'):
                    with mock.patch.object(getpass, 'getpass', lambda _: 'y'):
                        create.Create(cli.Cli())
        self.assertEqual(context.exception.msg, ERROR_MSGS['pwname'])

if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""This module tests the show module"""
import unittest
from libpkpass.commands.cli import Cli
from libpkpass.errors import DecryptionError, CliArgumentError
from .basetest.basetest import ERROR_MSGS, patch_args

class ShowErrors(unittest.TestCase):
    """This class tests the show class"""
    def test_decryption(self):
        """Test successful decryption"""
        ret = True
        try:
            with patch_args(subparser_name='show', identity='r1', nopassphrase='true',
                            all=None, pwname='test'):
                Cli().run()
        except DecryptionError:
            ret = False
        self.assertTrue(ret)

    def test_recipient_not_in_database(self):
        """test what happens when the recipient is not in the appropriate directory"""
        with self.assertRaises(CliArgumentError) as context:
            with patch_args(subparser_name='show', identity='bleh', nopassphrase='true',
                            all=None, pwname='test'):
                Cli().run()
        self.assertEqual(
            context.exception.msg,
            ERROR_MSGS['rep']
        )

    def test_showall_decryption(self):
        """Test showing all passwords"""
        ret = True
        try:
            with patch_args(subparser_name='show', identity='r1', nopassphrase='true',
                            all=True, pwname='*test*'):
                Cli().run()
        except DecryptionError:
            ret = False
        self.assertTrue(ret)

    def test_show_nopass_error(self):
        """Test what happens when neither pwname or the all flag are supplied"""
        ret = False
        try:
            with patch_args(subparser_name='show', identity='r1', nopassphrase='true',
                            all=None):
                "".join(Cli().run())
        except KeyError as error:
            if str(error) == "'pwname'":
                ret = str(error)
        self.assertEqual(ret, "'pwname'")

if __name__ == '__main__':
    unittest.main()

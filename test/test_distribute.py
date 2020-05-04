#!/usr/bin/env python
"""This module tests the distribute module"""
import builtins
import unittest
import argparse
import mock
import libpkpass.commands.cli as cli
import libpkpass.commands.distribute as distribute
from libpkpass.errors import CliArgumentError, DecryptionError
from .basetest.basetest import CONFIG

class DistributeTests(unittest.TestCase):
    """This class tests the distribute class"""
    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='distribute', identity='bleh',
                                                nopassphrase="true",
                                                pwname='test',
                                                config=CONFIG))
    def test_recipient_not_in_database(self, subparser_name):
        """test decryption functionality"""
        ret = False
        try:
            distribute.Distribute(cli.Cli())
        except CliArgumentError as error:
            if error.msg == "Error: Your user 'bleh' is not in the recipient database":
                ret = True
        self.assertTrue(ret)

    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='distribute', identity='r1',
                                                nopassphrase="true",
                                                pwname=None,
                                                config=CONFIG))
    def test_distribute_cli_error(self, subparser_name):
        """test decryption functionality"""
        ret = False
        try:
            distribute.Distribute(cli.Cli())
        except CliArgumentError as error:
            if error.msg == "'pwname' is a required argument":
                ret = True
        self.assertTrue(ret)

    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='distribute', identity='r1',
                                                nopassphrase="true",
                                                pwname='test',
                                                config=CONFIG))
    def test_distribute_cli_decrypt(self, subparser_name):
        """test decryption functionality"""
        ret = ""
        try:
            with mock.patch.object(builtins, 'input', lambda _: 'y'):
                distribute.Distribute(cli.Cli())
        except DecryptionError as error:
            ret = error.msg
        self.assertEqual(ret, "")


if __name__ == '__main__':
    unittest.main()

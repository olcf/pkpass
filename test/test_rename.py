#!/usr/bin/env python
"""This module tests the rename module"""
import unittest
import argparse
import mock
import libpkpass.commands.cli as cli
import libpkpass.commands.rename as rename
from libpkpass.errors import DecryptionError, CliArgumentError
from .basetest.basetest import CONFIG, BADPIN

class RenameTests(unittest.TestCase):
    """This class tests the rename class"""

    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='rename', identity='r1',
                                                nopassphrase="true",
                                                all=None,
                                                pwname='test',
                                                rename='retest',
                                                config=CONFIG))
    def test_safe_error(self, subparser_name):
        """test decryption functionality"""
        ret = False
        try:
            rename.Rename(cli.Cli())
        except DecryptionError:
            ret = True
        self.assertTrue(ret)

    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='rename', identity='bleh',
                                                nopassphrase="true",
                                                all=None,
                                                pwname='test',
                                                rename='retest',
                                                config=CONFIG))
    def test_recipient_not_in_database(self, subparser_name):
        """test decryption functionality"""
        ret = False
        try:
            rename.Rename(cli.Cli())
        except CliArgumentError as error:
            if error.msg == "Error: Your user 'bleh' is not in the recipient database":
                ret = True
        self.assertTrue(ret)

    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='rename', identity='r1',
                                                nopassphrase="true",
                                                all=True,
                                                pwname='test',
                                                rename='retest',
                                                overwrite="true",
                                                config=CONFIG))
    def test_rename_decryption_error(self, subparser_name):
        """test decryption functionality"""
        ret = False
        try:
            rename.Rename(cli.Cli())
        except DecryptionError as error:
            if error.msg == BADPIN:
                ret = True
        self.assertTrue(ret)

    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='rename', identity='r1',
                                                nopassphrase="true",
                                                all=True,
                                                pwname='test',
                                                overwrite="true",
                                                config=CONFIG))
    def test_rename_cli_error(self, subparser_name):
        """test decryption functionality"""
        ret = False
        try:
            rename.Rename(cli.Cli())
        except CliArgumentError as error:
            if error.msg == "'rename' is a required argument":
                ret = True
        self.assertTrue(ret)

if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python
"""This module tests the show module"""

import unittest
import argparse
import mock
import libpkpass.commands.cli as cli
import libpkpass.commands.show as show
from libpkpass.errors import DecryptionError, CliArgumentError

BADPIN = "Error decrypting password named 'test'.  Perhaps a bad pin/passphrase?"

class ShowErrors(unittest.TestCase):
    """This class tests the show class"""

    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='show', identity='r1',
                                                nopassphrase="true",
                                                all=None,
                                                pwname='test',
                                                config='./test/.test_config'))
    def test_decryption_error(self, subparser_name):
        """test decryption functionality"""
        ret = False
        try:
            show.Show(cli.Cli())
        except DecryptionError as error:
            if error.msg == BADPIN:
                ret = True
        self.assertTrue(ret)

    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='show', identity='bleh',
                                                nopassphrase="true",
                                                all=None,
                                                pwname='test',
                                                config='./test/.test_config'))
    def test_recipient_not_in_database(self, subparser_name):
        """test decryption functionality"""
        ret = False
        try:
            show.Show(cli.Cli())
        except CliArgumentError as error:
            if error.msg == "Error: Your user 'bleh' is not in the recipient database":
                ret = True
        self.assertTrue(ret)

    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='show', identity='r1',
                                                nopassphrase="true",
                                                all=True,
                                                pwname='test',
                                                config='./test/.test_config'))
    def test_showall_decryption_error(self, subparser_name):
        """test decryption functionality"""
        ret = False
        try:
            show.Show(cli.Cli())
        except DecryptionError as error:
            if error.msg == BADPIN:
                ret = True
        self.assertTrue(ret)

    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='show', identity='r1',
                                                nopassphrase="true",
                                                all=None,
                                                config='./test/.test_config'))
    def test_show_nopass_error(self, subparser_name):
        """test decryption functionality"""
        ret = False
        try:
            show.Show(cli.Cli())
        except KeyError as error:
            if error.message == "pwname":
                ret = True
        self.assertTrue(ret)


if __name__ == '__main__':
    unittest.main()

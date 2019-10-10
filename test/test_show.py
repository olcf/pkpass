#!/usr/bin/env python
"""This module tests the show module"""

from __future__ import absolute_import
import unittest
import argparse
import mock
import libpkpass.commands.cli as cli
import libpkpass.commands.show as show
from libpkpass.errors import DecryptionError, CliArgumentError
from .basetest.basetest import CONFIG, BADPIN

class ShowErrors(unittest.TestCase):
    """This class tests the show class"""

    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='show', identity='r1',
                                                nopassphrase="true",
                                                all=None,
                                                pwname='test',
                                                config=CONFIG))
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
                                                config=CONFIG))
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
                                                pwname='*test*',
                                                config=CONFIG))
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
                                                config=CONFIG))
    def test_show_nopass_error(self, subparser_name):
        """test decryption functionality"""
        ret = False
        try:
            show.Show(cli.Cli())
        except KeyError as error:
            if str(error) == "'pwname'":
                ret = str(error)
        self.assertEqual(ret, "'pwname'")


if __name__ == '__main__':
    unittest.main()

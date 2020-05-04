#!/usr/bin/env python
"""This module tests the create module"""
import getpass
import builtins
import unittest
import argparse
import mock
import libpkpass.commands.cli as cli
import libpkpass.commands.create as create
from libpkpass.errors import CliArgumentError, DecryptionError
from .basetest.basetest import CONFIG

class CreateTests(unittest.TestCase):
    """This class tests the create class"""
    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='create', identity='r1',
                                                nopassphrase="true",
                                                pwname='test',
                                                config=CONFIG))
    def test_create_success(self, subparser_name):
        """test decryption functionality"""
        ret = ""
        try:
            with mock.patch.object(builtins, 'input', lambda _: 'y'):
                with mock.patch.object(getpass, 'getpass', lambda _: 'y'):
                    create.Create(cli.Cli())
        except DecryptionError as error:
            ret = error.msg
        self.assertEqual(ret, "")

    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='create', identity='r1',
                                                nopassphrase="true",
                                                pwname=None,
                                                config=CONFIG))
    def test_create_no_pass(self, subparser_name):
        """test decryption functionality"""
        ret = ""
        try:
            with mock.patch.object(builtins, 'input', lambda _: 'y'):
                with mock.patch.object(getpass, 'getpass', lambda _: 'y'):
                    create.Create(cli.Cli())
        except CliArgumentError as error:
            ret = error.msg
        self.assertEqual(ret, "'pwname' is a required argument")


if __name__ == '__main__':
    unittest.main()

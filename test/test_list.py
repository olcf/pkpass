#!/usr/bin/env python
"""This module tests the list module"""

import unittest
import argparse
import mock
import libpkpass.commands.cli as cli
import libpkpass.commands.list as pklist
from libpkpass.errors import DecryptionError, CliArgumentError


class MockDevice():
    """Send stdout here"""
    def write(self, s): pass

class ListTests(unittest.TestCase):
    """This class tests the list class"""


    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='list', identity='bleh',
                                                nopassphrase="true",
                                                config='./test/.test_config'))
    def test_recipient_not_in_database(self, subparser_name):
        """test bad recipient functionality"""
        ret = False
        try:
            pklist.List(cli.Cli())
        except CliArgumentError as error:
            if error.msg == "Error: Your user 'bleh' is not in the recipient database":
                ret = True
        self.assertTrue(ret)

    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='list', identity='r1',
                                                nopassphrase="true",
                                                config='./test/.test_config'))
    def test_list(self, subparser_name):
        """test list functionality"""
        ret = False
        try:
            #this is not a good test
            with mock.patch('sys.stdout', new=MockDevice()):
                pklist.List(cli.Cli())
            ret = True
        except Exception:
            ret = False
        self.assertTrue(ret)

if __name__ == '__main__':
    unittest.main()

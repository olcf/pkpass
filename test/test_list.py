#!/usr/bin/env python
"""This module tests the list module"""
import unittest
import argparse
import mock
import libpkpass.commands.cli as cli
import libpkpass.commands.list as pklist
from libpkpass.errors import CliArgumentError
from .basetest.basetest import CONFIG, captured_output

PASSWORD_LIST_0 = "Passwordsfor'r2':"
PASSWORD_LIST_1 = "Passwordsfor'r1':test/passwords/test:Distributor:r1Name:test"

class ListTests(unittest.TestCase):
    """This class tests the list class"""

    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='list', identity='bleh',
                                                nopassphrase="true",
                                                config=CONFIG,
                                                color="false"))
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
                return_value=argparse.Namespace(subparser_name='list', identity='r2',
                                                nopassphrase="true",
                                                config=CONFIG,
                                                color="false"))
    def test_list_none(self, subparser_name):
        """test list functionality"""
        ret = False
        with captured_output() as (out, _):
            pklist.List(cli.Cli())
        output = "".join(out.getvalue().strip().split())
        self.assertEqual(output, PASSWORD_LIST_0)

    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='list', identity='r1',
                                                nopassphrase="true",
                                                config=CONFIG,
                                                color="false"))
    def test_list_one(self, subparser_name):
        """test list functionality"""
        ret = False
        with captured_output() as (out, _):
            pklist.List(cli.Cli())
        output = "".join(out.getvalue().strip().split())
        self.assertEqual(output, PASSWORD_LIST_1)

if __name__ == '__main__':
    unittest.main()

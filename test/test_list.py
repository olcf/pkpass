#!/usr/bin/env python
"""This module tests the list module"""
import unittest
import yaml
import libpkpass.commands.cli as cli
import libpkpass.commands.list as pklist
from libpkpass.errors import CliArgumentError
from .basetest.basetest import captured_output, patch_args, ERROR_MSGS

class ListTests(unittest.TestCase):
    """This class tests the list class"""
    def setUp(self):
        self.password_list_0 = {
            "Passwords for 'r2'": None
        }
        self.password_list_1 = {
            "Passwords for 'r1'": None,
            'test/passwords/test': {
                'Distributor': 'r1',
                'Name': 'test'
            }
        }

    def test_recipient_not_in_database(self):
        """test bad recipient functionality"""
        with self.assertRaises(CliArgumentError) as context:
            with patch_args(subparser_name='list', identity='bleh', nopassphrase="true"):
                pklist.List(cli.Cli())
        self.assertEqual(
            context.exception.msg,
            ERROR_MSGS['rep']
        )

    def test_list_none(self):
        """test list functionality for no passwords"""
        with patch_args(subparser_name='list', identity='r2', nopassphrase="true"):
            with captured_output() as (out, _):
                pklist.List(cli.Cli())
        output = yaml.safe_load(out.getvalue().replace('\t', ' '))
        self.assertDictEqual(output, self.password_list_0)

    def test_list_one(self):
        """test list functionality for one password"""
        with patch_args(subparser_name='list', identity='r1', nopassphrase="true"):
            with captured_output() as (out, _):
                pklist.List(cli.Cli())
        output = yaml.safe_load(out.getvalue().replace('\t', ' '))
        self.assertDictEqual(output, self.password_list_1)

if __name__ == '__main__':
    unittest.main()

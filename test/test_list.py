#!/usr/bin/env python3
"""This module tests the list module"""
import unittest
import yaml
from libpkpass.commands.cli import Cli
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
                Cli()
        self.assertEqual(
            context.exception.msg,
            ERROR_MSGS['rep']
        )

    def test_list_none(self):
        """test list functionality for no passwords"""
        with patch_args(subparser_name='list', identity='r2', nopassphrase="true"):
            with captured_output() as (out, _):
                Cli()
        out = "\n".join(out.getvalue().split('\n')[1:]).replace('\t', ' ')
        output = yaml.safe_load(out)
        self.assertDictEqual(output, self.password_list_0)

    def test_list_one(self):
        """test list functionality for one password"""
        with patch_args(subparser_name='list', identity='r1', nopassphrase="true"):
            with captured_output() as (out, _):
                Cli()
        out = "\n".join(out.getvalue().split('\n')[1:]).replace('\t', ' ')
        output = yaml.safe_load(out)
        self.assertDictEqual(output, self.password_list_1)

if __name__ == '__main__':
    unittest.main()

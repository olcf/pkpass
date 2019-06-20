#!/usr/bin/env python
"""This module tests the list module"""

import unittest
import argparse
import sys
from contextlib import contextmanager
# Python2/3 issues
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import mock
import libpkpass.commands.cli as cli
import libpkpass.commands.list as pklist
from libpkpass.errors import CliArgumentError

PASSWORD_LIST = "Passwordsfor'r1':test/passwords/test:distributor:ginsburgnmname:test"

@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

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
        with captured_output() as (out, _):
            pklist.List(cli.Cli())
        output = "".join(out.getvalue().strip().split())
        if output == PASSWORD_LIST:
            ret = True
        self.assertTrue(ret)

if __name__ == '__main__':
    unittest.main()

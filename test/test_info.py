#!/usr/bin/env python
"""This module tests the info module"""
import unittest
import argparse
import mock
import libpkpass.commands.cli as cli
import libpkpass.commands.info as info
from libpkpass.errors import CliArgumentError
from .basetest.basetest import CONFIG, captured_output

class InfoTests(unittest.TestCase):
    """This class tests the info class"""
    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='info', identity='r1',
                                                nopassphrase="true",
                                                pwname='test',
                                                color=False,
                                                config=CONFIG))
    def test_info(self, subparser_name):
        """test decryption functionality"""
        with captured_output() as (out, _):
            info.Info(cli.Cli())
        output = "".join(out.getvalue().strip().split()).split("timestamp")[0]
        testout = "Metadata:Authorizer:yCreator:r1Description:yName:testSchemaversion:v1Signature:NoneRecipients:r1TotalRecipients:1Earliestdistribute"
        self.assertEqual(output, testout)

    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='info', identity='r1',
                                                nopassphrase="true",
                                                pwname=None,
                                                config=CONFIG))
    def test_info_no_pass(self, subparser_name):
        """test decryption functionality"""
        ret = False
        try:
            with captured_output() as (out, _):
                info.Info(cli.Cli())
            output = "".join(out.getvalue().strip().split())
        except CliArgumentError as err:
            if err.msg == "'pwname' is a required argument":
                ret = True
        self.assertTrue(ret)

if __name__ == '__main__':
    unittest.main()

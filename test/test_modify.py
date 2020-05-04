#!/usr/bin/env python
"""This module tests the modify module"""
import builtins
import unittest
import argparse
import mock
import libpkpass.commands.cli as cli
import libpkpass.commands.modify as modify
from libpkpass.errors import CliArgumentError, DecryptionError
from .basetest.basetest import CONFIG

class ModifyTests(unittest.TestCase):
    """This class tests the modify class"""
    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='modify', identity='r3',
                                                nopassphrase="true",
                                                pwname='gentest',
                                                config=CONFIG))
    def test_modify_success(self, subparser_name):
        """test decryption functionality"""
        ret = ""
        try:
            with mock.patch.object(builtins, 'input', lambda _: 'y'):
                modify.Modify(cli.Cli())
        except DecryptionError as error:
            ret = error.msg
        self.assertEqual(ret, "")


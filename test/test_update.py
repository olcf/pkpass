#!/usr/bin/env python
"""This module tests the update module"""
import getpass
import builtins
import unittest
import argparse
import mock
import libpkpass.commands.cli as cli
import libpkpass.commands.update as update
from libpkpass.errors import DecryptionError
from .basetest.basetest import CONFIG

class UpdateTests(unittest.TestCase):
    """This class tests the update class"""
    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='update', identity='r3',
                                                nopassphrase="true",
                                                pwname='gentest',
                                                config=CONFIG))
    def test_update_success(self, subparser_name):
        """test decryption functionality"""
        ret = ""
        try:
            with mock.patch.object(builtins, 'input', lambda _: 'y'):
                with mock.patch.object(getpass, 'getpass', lambda _: 'y'):
                    update.Update(cli.Cli())
        except DecryptionError as error:
            ret = error.msg
        self.assertEqual(ret, "")

#!/usr/bin/env python
"""This module tests the update module"""
import getpass
import builtins
import unittest
import mock
import libpkpass.commands.cli as cli
import libpkpass.commands.update as update
from libpkpass.errors import DecryptionError
from .basetest.basetest import patch_args

class UpdateTests(unittest.TestCase):
    """This class tests the update class"""
    def test_update_success(self):
        """Test a successful update of a password"""
        ret = True
        try:
            with patch_args(subparser_name='update', identity='r3', nopassphrase='true',
                            pwname='gentest'):
                with mock.patch.object(builtins, 'input', lambda _: 'y'):
                    with mock.patch.object(getpass, 'getpass', lambda _: 'y'):
                        update.Update(cli.Cli())
        except DecryptionError:
            ret = False
        self.assertTrue(ret)

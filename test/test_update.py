#!/usr/bin/env python3
"""This module tests the update module"""
import getpass
import builtins
import unittest
import mock
from libpkpass.commands.cli import Cli
from libpkpass.errors import DecryptionError
from .basetest.basetest import patch_args

class UpdateTests(unittest.TestCase):
    """This class tests the update class"""
    def test_update_success(self):
        """Test a successful update of a password"""
        ret = True
        try:
            with patch_args(subparser_name='update', identity='r3', nopassphrase='true',
                            pwname='gentest', no_cache=True):
                with mock.patch.object(builtins, 'input', lambda _: 'y'):
                    with mock.patch.object(getpass, 'getpass', lambda _: 'y'):
                        Cli().run()
        except DecryptionError:
            ret = False
        self.assertTrue(ret)

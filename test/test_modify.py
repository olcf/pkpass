#!/usr/bin/env python3
"""This module tests the modify module"""
import builtins
import unittest
import mock
from libpkpass.commands.cli import Cli
from libpkpass.errors import DecryptionError
from .basetest.basetest import patch_args

class ModifyTests(unittest.TestCase):
    """This class tests the modify class"""
    def test_modify_success(self):
        """Test modifying the metadata of a password"""
        ret = True
        try:
            with patch_args(subparser_name='modify', identity='r3', nopassphrase='true',
                            pwname='gentest'):
                with mock.patch.object(builtins, 'input', lambda _: 'y'):
                    Cli().run()
        except DecryptionError:
            ret = False
        self.assertTrue(ret)

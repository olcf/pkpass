#!/usr/bin/env python
"""This module tests the modify module"""
import builtins
import unittest
import mock
import libpkpass.commands.cli as cli
import libpkpass.commands.modify as modify
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
                    modify.Modify(cli.Cli())
        except DecryptionError:
            ret = False
        self.assertTrue(ret)

#!/usr/bin/env python
"""This module tests the rename module"""
import builtins
import unittest
import mock
import libpkpass.commands.cli as cli
import libpkpass.commands.rename as rename
from libpkpass.errors import DecryptionError, CliArgumentError
from .basetest.basetest import patch_args, ERROR_MSGS

class RenameTests(unittest.TestCase):
    """This class tests the rename class"""
    def test_recipient_not_in_database(self):
        """Test what happens when a recipient is not in the appropriate directory"""
        with self.assertRaises(CliArgumentError) as context:
            with patch_args(subparser_name='rename', identity='bleh', nopassphrase='true',
                            all=None, pwname='test', rename='retest'):
                rename.Rename(cli.Cli())
        self.assertEqual(
            context.exception.msg,
            ERROR_MSGS['rep']
        )

    def test_rename_success(self):
        """Test a successful rename (then rename it back)"""
        ret = True
        try:
            with patch_args(subparser_name='rename', identity='r1', nopassphrase='true',
                            all=True, pwname='test', rename='retest', overwrite='true'):
                with mock.patch.object(builtins, 'input', lambda _: 'y'):
                    rename.Rename(cli.Cli())
            with patch_args(subparser_name='rename', identity='r1', nopassphrase='true',
                            all=True, pwname='retest', rename='test', overwrite="true"):
                with mock.patch.object(builtins, 'input', lambda _: 'y'):
                    rename.Rename(cli.Cli())
        except DecryptionError:
            ret = False
        self.assertTrue(ret)

    def test_rename_cli_error(self):
        """Test what happens when pwname is not supplied"""
        with self.assertRaises(CliArgumentError) as context:
            with patch_args(subparser_name='rename', identity='r1', nopassphrase='true',
                            all=True, rename='test', overwrite='true'):
                rename.Rename(cli.Cli())
        self.assertEqual(context.exception.msg, ERROR_MSGS['pwname'])

if __name__ == '__main__':
    unittest.main()

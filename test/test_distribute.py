#!/usr/bin/env python3
"""This module tests the distribute module"""
import builtins
import unittest
import mock
import libpkpass.commands.cli as cli
import libpkpass.commands.distribute as distribute
from libpkpass.errors import CliArgumentError, DecryptionError
from .basetest.basetest import patch_args, ERROR_MSGS

class DistributeTests(unittest.TestCase):
    """This class tests the distribute class"""
    def test_recipient_not_in_database(self):
        """Test what happens with a recipient is not within the appropriate directory"""
        with self.assertRaises(CliArgumentError) as context:
            with patch_args(subparser_name='distribute', identity='bleh', nopassphrase='true',
                            pwname='test'):
                distribute.Distribute(cli.Cli())
        self.assertEqual(
            context.exception.msg,
            ERROR_MSGS['rep']
        )

    def test_distribute_cli_error(self):
        """Test what happens with pwname is not supplied"""
        with self.assertRaises(CliArgumentError) as context:
            with patch_args(subparser_name='distribute', identity='r1', nopassphrase='true',
                            pwname=None):
                distribute.Distribute(cli.Cli())
        self.assertEqual(context.exception.msg, ERROR_MSGS['pwname'])

    def test_distribute_success(self):
        """Test a successful distribute"""
        ret = True
        try:
            with patch_args(subparser_name='distribute', identity='r1', nopassphrase='true',
                            pwname='test'):
                with mock.patch.object(builtins, 'input', lambda _: 'y'):
                    distribute.Distribute(cli.Cli())
        except DecryptionError:
            ret = False
        self.assertTrue(ret)


if __name__ == '__main__':
    unittest.main()

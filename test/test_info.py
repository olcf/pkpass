#!/usr/bin/env python
"""This module tests the info module"""
import unittest
import yaml
import libpkpass.commands.cli as cli
import libpkpass.commands.info as info
from libpkpass.errors import CliArgumentError
from .basetest.basetest import captured_output, patch_args, ERROR_MSGS

class InfoTests(unittest.TestCase):
    """This class tests the info class"""
    def setUp(self):
        self.check_dict = {
            'Metadata': {
                'Authorizer': 'y',
                'Creator': 'r1',
                'Description': 'y',
                'Name': 'test',
                'Schemaversion': 'v1',
                'Signature': 'None'
            },
            'Recipients': 'r1',
            'Total Recipients': 1,
        }

    def test_info(self):
        """Test what info shows on a password"""
        with patch_args(subparser_name='info', identity='r1',
                        nopassphrase="true", pwname='test'):
            with captured_output() as (out, _):
                info.Info(cli.Cli())
        output = yaml.safe_load(out.getvalue())
        del output['Earliest distribute timestamp']
        self.assertDictEqual(output, self.check_dict)

    def test_info_no_pass(self):
        """Test what happens when pwname is not supplied"""
        with patch_args(subparser_name='info', identity='r1',
                        nopassphrase="true", pwname=None):
            with self.assertRaises(CliArgumentError) as context:
                info.Info(cli.Cli())
        self.assertEqual(context.exception.msg, ERROR_MSGS['pwname'])

if __name__ == '__main__':
    unittest.main()

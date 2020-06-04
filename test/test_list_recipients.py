#!/usr/bin/env python
"""This module tests the listrecipients module"""
import unittest
import yaml
import libpkpass.commands.cli as cli
import libpkpass.commands.listrecipients as listrecipients
from .basetest.basetest import captured_output, patch_args

class ListrecipientsTests(unittest.TestCase):
    """This class tests the listrecipients class"""
    def setUp(self):
        self.out_dict = {
            'Certificate store': 'test/pki/intermediate/certs',
            'Key store': 'test/pki/intermediate/private',
            'CA Bundle file': 'test/pki/intermediate/certs/ca-bundle',
            'Looking for Key Extension': '.key',
            'Looking for Certificate Extension': "['.cert', '.crt']",
            'Loaded 4 identities': None,
            'r3': {
                'certs': {
                    'verified': True,
                }
            }
        }

    def test_listrecipients(self):
        """Test a listing of our recipients"""
        self.maxDiff = None
        with patch_args(subparser_name='listrecipients', identity='r1',
                        nopassphrase="true", filter="r3"):
            with captured_output() as (out, _):
                listrecipients.Listrecipients(cli.Cli())
        output = yaml.safe_load(out.getvalue().replace('\t', '  '))
        # we remove these things because the actual values depend on creation
        # moreover, some of the outputs on different operating systems appear
        # to utilize different delimiters.
        del output['r3']['certs']['enddate']
        del output['r3']['certs']['subjecthash']
        del output['r3']['certs']['issuerhash']
        del output['r3']['certs']['fingerprint']
        del output['r3']['certs']['subject']
        del output['r3']['certs']['issuer']
        self.assertDictEqual(output, self.out_dict)

if __name__ == '__main__':
    unittest.main()

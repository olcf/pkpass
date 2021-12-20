#!/usr/bin/env python3
"""This module tests the listrecipients module"""
import logging
import unittest
import yaml
from libpkpass.commands.cli import Cli
from .basetest.basetest import patch_args

class ListrecipientsTests(unittest.TestCase):
    """This class tests the listrecipients class"""
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.out_dict = {
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
            out = "\n".join(Cli().run()).replace('\t', ' ')
        output = yaml.safe_load(out)
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

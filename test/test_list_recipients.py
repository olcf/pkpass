#!/usr/bin/env python
"""This module tests the listrecipients module"""
import unittest
import argparse
import mock
import libpkpass.commands.cli as cli
import libpkpass.commands.listrecipients as listrecipients
from .basetest.basetest import CONFIG, captured_output

class ListrecipientsTests(unittest.TestCase):
    """This class tests the listrecipients class"""
    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(subparser_name='listrecipients', identity='r1',
                                                nopassphrase="true",
                                                pwname='test',
                                                color=False,
                                                filter="r3",
                                                config=CONFIG))
    def test_listrecipients(self, subparser_name):
        """test decryption functionality"""
        with captured_output() as (out, _):
            listrecipients.Listrecipients(cli.Cli())
        output = "".join(out.getvalue().strip().split()).split("subject")[0]
        testout = 'Certificatestore:"test/pki/intermediate/certs"Keystore:"test/pki/intermediate/private"CABundlefile:"test/pki/intermediate/certs/ca-bundle"LookingforKeyExtension:".key"LookingforCertificateExtension:"[\'.cert\',\'.crt\']"Loaded4identities:r3:certs:verified:True'
        self.assertEqual(output, testout)

if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""This module tests the info module"""
import unittest
import pylibyaml  # pylint: disable=unused-import
import yaml
from libpkpass.commands.cli import Cli
from libpkpass.errors import CliArgumentError
from .basetest.basetest import patch_args, ERROR_MSGS


class InfoTests(unittest.TestCase):
    """This class tests the info class"""

    def setUp(self):
        self.check_dict = {
            "Metadata": {
                "Authorizer": "y",
                "Creator": "r1",
                "Description": "y",
                "Name": "test",
                "Schemaversion": "v2",
                "Signature": "None",
            },
            "Escrow Group": {
                "Creator": "r1",
                "Share Holders": "r2, r3, r4",
                "Total Group Share Holders": 3,
                "Minimum_escrow": 2,
            },
            "Recipients": "r1",
            "Total Recipients": 1,
        }

    def test_info(self):
        """Test what info shows on a password"""
        with patch_args(
            subparser_name="info", identity="r1", nopassphrase="true", pwname="test"
        ):
            out = "\n".join(Cli().run())
        output = yaml.safe_load(out)
        del output["Earliest distribute timestamp"]
        del output["Escrow Group"]["Group creation time"]
        self.assertDictEqual(output, self.check_dict)

    def test_info_no_pass(self):
        """Test what happens when pwname is not supplied"""
        with patch_args(
            subparser_name="info", identity="r1", nopassphrase="true", pwname=None
        ):
            with self.assertRaises(CliArgumentError) as context:
                "".join(Cli().run())
        self.assertEqual(context.exception.msg, ERROR_MSGS["pwname"])


if __name__ == "__main__":
    unittest.main()

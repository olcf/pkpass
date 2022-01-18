#!/usr/bin/env python3
"""This module tests the show module"""
import sys
import io
import unittest
from unittest.mock import patch
from libpkpass.commands.cli import Cli
from libpkpass.errors import DecryptionError, CliArgumentError

# from libpkpass.escrow import pk_recover_secret
from .basetest.basetest import ERROR_MSGS, patch_args


class ShowErrors(unittest.TestCase):
    """This class tests the show class"""

    def test_decryption(self):
        """Test successful decryption"""
        ret = True
        try:
            with patch_args(
                subparser_name="show",
                identity="r1",
                nopassphrase="true",
                all=None,
                pwname="test",
            ):
                "".join(Cli().run())
        except DecryptionError:
            ret = False
        self.assertTrue(ret)

    def test_recipient_not_in_database(self):
        """test what happens when the recipient is not in the appropriate directory"""
        with self.assertRaises(CliArgumentError) as context:
            with patch_args(
                subparser_name="show",
                identity="bleh",
                nopassphrase="true",
                all=None,
                pwname="test",
            ):
                Cli().run()
        self.assertEqual(context.exception.msg, ERROR_MSGS["rep"])

    def test_showall_decryption(self):
        """Test showing all passwords"""
        ret = True
        try:
            with patch_args(
                subparser_name="show",
                identity="r1",
                nopassphrase="true",
                all=True,
                pwname="*test*",
            ):
                Cli().run()
        except DecryptionError:
            ret = False
        self.assertTrue(ret)

    def test_show_nopass_error(self):
        """Test what happens when neither pwname or the all flag are supplied"""
        ret = False
        try:
            with patch_args(
                subparser_name="show", identity="r1", nopassphrase="true", all=None
            ):
                "".join(Cli().run())
        except KeyError as error:
            if str(error) == "'pwname'":
                ret = str(error)
        self.assertEqual(ret, "'pwname'")

    def test_show_recovery(self):
        try:
            shares = []
            with patch_args(
                pwname="test",
                subparser_name="show",
                identity="r2",
                nopassphrase=True,
                all=None,
                recovery="true",
            ):
                shares.append("".join(Cli().run()).split("test: ")[1])
                print(shares)
            with patch_args(
                pwname="test",
                subparser_name="show",
                identity="r3",
                nopassphrase=True,
                all=None,
                recovery="true",
            ):
                shares.append("".join(Cli().run()).split("test: ")[1])
            with patch_args(
                pwname="test",
                subparser_name="recover",
                identity="r3",
                nopassphrase=True,
            ):
                with unittest.mock.patch(
                    "builtins.input", return_value=",".join(shares)
                ):
                    passwd = "|".join(Cli().run())
        except DecryptionError as err:
            raise err
        self.assertEqual(passwd.split("|")[1], "y")


if __name__ == "__main__":
    unittest.main()

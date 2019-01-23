#!/usr/bin/env python
"""This module tests the recover module"""

import unittest
import libpkpass.escrow as escrow

class EscrowTests(unittest.TestCase):
    """This class tests the recover class"""
    shares = escrow.pk_split_secret("boomtown", ["r1", "r2", "r3"], 2)

    def test_split_secret_all_shares(self):
        """test recovery with all shares functionality"""
        passwd = escrow.pk_recover_secret(self.shares)
        self.assertEqual(passwd, "boomtown")

    def test_split_secret_min_shares(self):
        """test recovery with min shares functionality"""
        passwd = escrow.pk_recover_secret(self.shares[0:2])
        self.assertEqual(passwd, "boomtown")

    def test_split_secret_failure(self):
        """test recovery failure with not enough shares"""
        passwd = escrow.pk_recover_secret(self.shares[0:1])
        self.assertNotEqual(passwd, "boomtown")

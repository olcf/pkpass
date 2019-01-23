#!/usr/bin/env python
"""This Module handles the escrow functions i.e. creating shares and recovery"""

from secretsharing import PlaintextToHexSecretSharer as ptohss

##############################################################################
def pk_split_secret(plaintext_string, escrow_list, minimum=None):
    """split a secret into multiple shares for encryption"""
##############################################################################
    escrow_len = len(escrow_list)
    if not minimum and escrow_len % 2 != 0:
        minimum = (escrow_len + 1) / 2
    elif not minimum:
        minimum = (escrow_len / 2) + 1
    return ptohss.split_secret(plaintext_string, minimum, escrow_len)

##############################################################################
def pk_recover_secret(shares):
    """Take Decrypted strings from crypto and recover a secret"""
##############################################################################
    return ptohss.recover_secret(shares)

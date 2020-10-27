#!/usr/bin/env python3
"""This Module handles the escrow functions i.e. creating shares and recovery"""
from pyseltongue import PlaintextToHexSecretSharer as ptohss
from .errors import EscrowError

    ##############################################################################
def pk_split_secret(plaintext_string, escrow_list, minimum=None):
    """split a secret into multiple shares for encryption"""
    ##############################################################################
    escrow_len = len(escrow_list)
    if not minimum and escrow_len % 2 != 0:
        minimum = int((escrow_len + 1) / 2)
    elif not minimum:
        minimum = int((escrow_len / 2) + 1)
    if minimum < 2:
        raise EscrowError("minimum escrow", 2, minimum)
    if escrow_len < 3:
        raise EscrowError("escrow users list", 3, escrow_len)
    return ptohss.split_secret(str(plaintext_string), minimum, escrow_len)

    ##############################################################################
def pk_recover_secret(shares):
    """Take Decrypted strings from crypto and recover a secret"""
    ##############################################################################
    return ptohss.recover_secret(shares)

#!/usr/bin/env python3
"""This module provides base testing capabilites"""
import sys
import argparse
from contextlib import contextmanager
from io import StringIO
import mock

CONFIG = './test/.test_config'
BADPIN = "Error decrypting password named 'test'.  Perhaps a bad pin/passphrase?"
ERROR_MSGS = {
    'pwname': "'pwname' is a required argument",
    'rep': "Error: Your user 'bleh' is not in the recipient database",
}

@contextmanager
def captured_output():
    """capture stdout and stderr for use of parsing pkpass output"""
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

def patch_args(**kwargs):
    """Patch argparse arguments intended for use with `with` statement
    uses default config path and no color output"""
    return mock.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=argparse.Namespace(
            config=CONFIG, color=False,
            **kwargs
        )
    )

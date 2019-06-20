#!/usr/bin/env python
"""This module provides base testing capabilites"""
import sys
from contextlib import contextmanager
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

global CONFIG
CONFIG = './test/.test_config'
global BADPIN
BADPIN = "Error decrypting password named 'test'.  Perhaps a bad pin/passphrase?"

@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

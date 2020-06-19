#!/usr/bin/env python3
"""This Module handles the CLI and any error that comes from it"""
import sys
if sys.version_info[0] < 3:
    raise Exception('Python version 3 is required 3.5 and higher is actively tested')

# pylint: disable=wrong-import-position
# Reasoning for the disablement is because we want people to not try to run with python2
import argparse
from traceback import format_exception_only
from libpkpass.errors import PKPassError
from libpkpass.commands.cli import Cli

PARSER = argparse.ArgumentParser(add_help=False)
# This debug flag exists in both this parser and the main parser
# of Cli
PARSER.add_argument("--debug", action='store_true')
HIGH_LEVEL_ARGS, ARGS = PARSER.parse_known_args()
try:
    Cli()
except PKPassError as error:
    print("\n\n%s: %s" % (str(type(error).__name__), error.msg))
except KeyboardInterrupt:
    print("\nExiting")
# This is so that users don't see tracebacks, an error will still print out
# so that we can investigate
# Comment this out for debugging
except Exception as err: # pylint: disable=broad-except
    if HIGH_LEVEL_ARGS.debug:
        raise err
    print("Generic exception caught: \n\t%s" %
          format_exception_only(type(err), err)[0])

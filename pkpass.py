#!/usr/bin/env python
"""This Module handles the CLI and any error that comes from it"""

from __future__ import print_function
from libpkpass.errors import PKPassError
from libpkpass.commands.cli import Cli

try:
    Cli()
except PKPassError as error:
    print("\n\n%s: %s" % (str(type(error).__name__), error.msg))
except KeyboardInterrupt:
    print("\nExiting")

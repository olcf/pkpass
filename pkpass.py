#!/usr/bin/env python
"""This Module handles the CLI and any error that comes from it"""

from libpkpass.errors import *

from libpkpass.commands.cli import Cli

try:
    Cli()
except PKPassError as error:
    print "\n\n%s: %s" % (str(type(error).__name__), error.msg)
except KeyboardInterrupt:
    print "\nExiting"

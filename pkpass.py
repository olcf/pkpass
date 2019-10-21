#!/usr/bin/env python
"""This Module handles the CLI and any error that comes from it"""

from __future__ import print_function
import traceback
from libpkpass.errors import PKPassError
from libpkpass.commands.cli import Cli

try:
    Cli()
except PKPassError as error:
    print("\n\n%s: %s" % (str(type(error).__name__), error.msg))
except KeyboardInterrupt:
    print("\nExiting")
# Comment this out for debugging
except Exception as err:
    if str(err):
        print(err)
    else:
        print("Generic exception caught: \n%s" %
              traceback.format_exception_only(type(err), err)[0])

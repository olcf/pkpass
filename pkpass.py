#!/usr/bin/env python

from libpkpass.errors import *

from libpkpass.commands.cli import Cli

try:
  Cli()
except PKPassError as e:
  print("\n\n%s: %s" % (str(type(e).__name__), e.msg))
except KeyboardInterrupt:
  print("\nExiting")

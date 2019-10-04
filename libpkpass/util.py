#!/usr/bin/env python

from colorama import Fore

def color_prepare(string, color, colorize):
    return "%s%s%s" % (color, string, Fore.RESET) if colorize else string

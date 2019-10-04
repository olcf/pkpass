#!/usr/bin/env python

import sys
import re
import fnmatch
import argparse
# from colored import fore, style
from colored import fg, attr

####################################################################
def color_prepare(string, color_type, colorize, theme_map=None):
####################################################################
    if theme_map is None:
        theme_map = {}
    color_defaults = {
        "info": "cyan",
        "warning": "yellow",
        "debug": "red",
        "first_level": "magenta",
        "second_level": "green"
    }
    color = theme_map[color_type].lower() if (color_type in theme_map) else color_defaults[color_type]
    try:
        return "%s%s%s" % (fg(color), string, attr('reset')) if colorize else string
    except KeyError:
        return "%s%s%s" % (fg(color_defaults[color_type]), string, attr('reset')) if colorize else string


####################################################################
def set_default_subparser(self, name, args=None, positional_args=0):
    """Set default subparser to interpreter"""
####################################################################
    subparser_found = False
    for arg in sys.argv[1:]:
        if arg in ['-h', '--help']:
            break
    else:
        for action in self._subparsers._actions:
            if not isinstance(action, argparse._SubParsersAction):
                continue
            for _ in sys.argv[1:]:
                subparser_found = True
        if not subparser_found:
            if args is None:
                sys.argv.insert(len(sys.argv) - positional_args, name)
            else:
                args.insert(len(args) - positional_args, name)

####################################################################
def show_version():
####################################################################
    try:
        version = ""
        with open("VERSION", 'r') as version_file:
            version = version_file.read().strip()
        return version
    except IOError as err:
        return err

####################################################################
def sort(lst):
    """Sort our alphanumeric keys"""
####################################################################
    lst = [str(i) for i in lst]
    lst.sort()
    return [int(i) if i.isdigit() else i for i in lst]

####################################################################
def dictionary_filter(string_match, dictionary, secondary_check=None):
    """Filter out our dictionary"""
####################################################################
    key_list = []
    key_list = fnmatch.filter(dictionary.keys(), string_match)

    # If not a fileglob match, try regex
    if not key_list:
        try:
            key_list = [k for k in dictionary.keys() if re.search(string_match, k)]
        except re.error as err:
            print(err)

    if not secondary_check:
        return {k: dictionary[k] for k in key_list}
    return {k: dictionary[k] for k in key_list
            if secondary_check[0] in dictionary[k][secondary_check[1]].keys()}

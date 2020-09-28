#!/usr/bin/env python3
"""General Utility file for common functionality"""
from os import path
from json import loads
from getpass import getuser
from sys import argv
from re import search, error
from fnmatch import filter as fnfilter
from argparse import _SubParsersAction
from yaml import safe_load
from yaml.parser import ParserError
from yaml.scanner import ScannerError
from colored import fg, attr
from libpkpass import __version__
from libpkpass.errors import FileOpenError, JsonArgumentError, ConfigParseError

    ####################################################################
def color_prepare(string, color_type, colorize, theme_map=None):
    """Handle the color output of a given string"""
    ####################################################################
    if theme_map is None:
        theme_map = {}
    color_defaults = {
        "info": "cyan",
        "warning": "yellow",
        "debug": "red",
        "first_level": "magenta",
        "second_level": "green",
        "third_level": "blue"
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
    for arg in argv[1:]:
        if arg in ['-h', '--help']:
            break
    else:
        # pylint: disable=protected-access
        # disabling protected access because subparsers are protected
        # and we want to be able to have a default subparser
        for action in self._subparsers._actions:
            if not isinstance(action, _SubParsersAction):
                continue
            for _ in argv[1:]:
                subparser_found = True
        if not subparser_found:
            if args is None:
                argv.insert(len(argv) - positional_args, name)
            else:
                args.insert(len(args) - positional_args, name)

    ####################################################################
def show_version():
    """return the version number in the VERSION file"""
    ####################################################################
    return __version__

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
    key_list = fnfilter(dictionary.keys(), string_match)

    # If not a fileglob match, try regex
    if not key_list:
        try:
            key_list = [k for k in dictionary.keys() if search(string_match, k)]
        except error as err:
            print(err)

    if not secondary_check:
        return {k: dictionary[k] for k in key_list}
    return {k: dictionary[k] for k in key_list
            if secondary_check[0] in dictionary[k][secondary_check[1]].keys()}

    ##################################################################
def handle_filepath_args(args):
    """Does filepath expansion for config args"""
    ##################################################################
    file_path_args = ['cabundle', 'pwstore', 'certpath', 'keypath']
    for arg in file_path_args:
        if arg in args and args[arg]:
            args[arg] = path.expanduser(args[arg])
    if 'connect' in args and args['connect'] and \
            'base_directory' in args['connect'] and args['connect']['base_directory']:
        args['connect']['base_directory'] = path.expanduser(args['connect']['base_directory'])
    return args

    ##################################################################
def handle_boolean_args(args, argname):
    ##################################################################
    if isinstance(args[argname], str):
        return args[argname].upper() == 'TRUE'
    return args[argname]

    ##################################################################
def convert_strings_to_list(args, argname):
    """ convert argparsed strings to lists for an argument """
    ##################################################################
    if argname in args:
        args[argname] = args[argname].split(",") if args[argname] else []
        return [arg.strip() for arg in args[argname] if arg.strip()]
    return []

    ##################################################################
def parse_json_arguments(args, argument):
    """ Parses the json.loads arguments as dictionaries to use"""
    ##################################################################
    try:
        if argument in args and args[argument]:
            if isinstance(args[argument], dict):
                return args[argument]
            return loads(args[argument])
        return None
    except ValueError as err:
        raise JsonArgumentError(argument, err)

    ##################################################################
def collect_args(parsedargs):
    ##################################################################
    # Build a dict out of the argparse args Namespace object and a dict from any
    # configuration files and merge the two with cli taking priority
    args = {
        'ignore_decrypt': False,
        'identity': getuser(),
        'cabundle': './certs/ca-bundle',
        'keypath': './private',
        'pwstore': './passwords',
        'time': 10,
        'card_slot': None,
        'certpath': None,
        'escrow_users': None,
        'min_escrow': None,
        'no_cache': False,
        'noverify': None,
        'noescrow': False,
        'overwrite': False,
        'recovery': False,
        'rules': 'default',
        'theme_map': None,
        'color': True,
        'verbosity': 0,
    }
    cli_args = parsedargs if isinstance(parsedargs, dict) else vars(parsedargs)
    config_args = get_config_args(cli_args['config'], cli_args)
    args.update(config_args)
    args['connect'] = parse_json_arguments(args, 'connect')
    args = handle_filepath_args(args)

    fles = ['cabundle', 'pwstore']
    for key, value in cli_args.items():
        if value is not None or key not in args:
            args[key] = value
        if key in fles and not path.exists(args[key]):
            raise FileOpenError(args[key], "No such file or directory")

    # json args
    args['color'] = handle_boolean_args(args, 'color')
    args['groups'] = convert_strings_to_list(args, 'groups')
    args['users'] = convert_strings_to_list(args, 'users')
    args['escrow_users'] = convert_strings_to_list(args, 'escrow_users')
    return args

    ##################################################################
def get_config_args(config, cli_args):
    """Return the configuration from the config file"""
    ##################################################################
    try:
        with open(config, 'r') as fname:
            config_args = safe_load(fname)
        if config_args is None:
            config_args = {}
        return config_args
    except IOError:
        if cli_args['verbosity'] != -1:
            print("INFO: No .pkpassrc file found")
        return {}
    except (ParserError, ScannerError):
        raise ConfigParseError("Parsing error with config file, please check syntax")

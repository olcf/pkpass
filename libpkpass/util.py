#!/usr/bin/env python3
"""General Utility file for common functionality"""
from os import path
from tempfile import gettempdir
from json import loads
from getpass import getuser
from sys import argv
from re import search, error
from fnmatch import filter as fnfilter
from argparse import _SubParsersAction
from sqlalchemy import create_engine
from yaml import safe_load
from yaml.parser import ParserError
from yaml.scanner import ScannerError
from colored import fg, attr
from libpkpass import __version__
from libpkpass.models import Base
from libpkpass.models.recipient import Recipient
from libpkpass.models.cert import Cert
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
        return f"{fg(color)}{string}{attr('reset')}" if colorize else string
    except KeyError:
        return f"{fg(color_defaults[color_type])}{string}{attr('reset')}" if colorize else string


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
    yield __version__

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
        raise JsonArgumentError(argument, err) from err

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
        'stdin': False,
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
    return setup_db(args)

    ##################################################################
def setup_db(args):
    """Setup global db engine"""
    ##################################################################
    if args['connect'] and 'base_directory' in args['connect']:
        db_path = path.join(args['connect']['base_directory'], 'rd.db')
    elif 'certpath' in args and args['certpath']:
        db_path = path.join(args['certpath'], 'rd.db')
    else:
        db_path = path.join(gettempdir(), 'rd.db')
    args['db'] = {}
    args['db']['uri'] = f"sqlite+pysqlite:///{db_path}"
    args['db']['engine'] = create_engine(args['db']['uri'])
    Base.metadata.create_all(args['db']['engine'])
    return args

    ##################################################################
def get_config_args(config, cli_args):
    """Return the configuration from the config file"""
    ##################################################################
    try:
        with open(config, 'r', encoding='ASCII') as fname:
            config_args = safe_load(fname)
        return config_args if config_args else {}
    except IOError:
        if cli_args['verbosity'] != -1:
            print("INFO: No .pkpassrc file found")
        return {}
    except (ParserError, ScannerError) as err:
        raise ConfigParseError("Parsing error with config file, please check syntax") from err

    ###################################################################
def create_or_update(session, model, unique_identifiers=None,
                     dont_update=None, **kwargs):
    """Create db object if it doesn't exist, doesn't commit to db
    updates existing objects, returns the object

    session: database session to utilize,
    model: sqlalchemy model to query on
    dont_update: list of keys in kwargs that should be ignored if the record alredy exists,
        this would generally be an ID that is a permanent record id from an external data
        source
    unique_identifiers: list of the keys in 'kwargs' that identify a unique instance
    kwargs: key, value pair of columns in the database model
    """
    ###################################################################
    # Remove parameters that do not exist in the model
    # this indicates the source has updated what it sends
    if not unique_identifiers:
        # If there are not unique_identifiers listed, utilize the whole
        # object as a unique item
        query_params = kwargs
    else:
        # If unique identifiers do exit filter the kwargs down by that list
        # and then get the instance that matches that
        query_params = {k:v for k,v in kwargs.items() if k in unique_identifiers}
    instance = session.query(model).filter_by(**query_params).first()
    # If we do not have an instance yet this means that we need
    # to create a new object
    if not instance:
        session.add(model(**kwargs))
        instance = session.query(model).filter_by(**query_params).first()
    # If we do have an instance at this point, we need to ensure
    # That the new data we recieved from the data source is
    # appropriately populated in that row
    else:
        dont_update = dont_update if dont_update else []
        for key, value in kwargs.items():
            if key not in dont_update:
                setattr(instance, key, value)
    return instance

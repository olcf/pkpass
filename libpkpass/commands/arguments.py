"""This Module defines the arguments that argparse will accept from the CLI"""
from json import loads

ARGUMENTS = {
    ############################################################################
    # Data structure containing all arguments a user could pass into pkpass
    # This helps us de-dupe our work and keep args consistent between
    # subcommands.  We use this with *args and **kwargs constructs
    ############################################################################
    'all': {
        'args': ['-a', '--all'],
        'kwargs': {
            'help': "Show all available password to the given user, if a pwname is supplied filtering will be done case-insensitivey based on the filename",
            'action': "store_true"
        }
    },

    'authorizer': {
        'args': ['--authorizer'],
        'kwargs': {
            'help': "The person or account authorizing the creation of this secret",
            'type': str
        }
    },

    'behalf': {
        'args': ['-b', '--behalf'],
        'kwargs': {
            'help': 'Show passwords for a user using a password as its private key',
            'type': str,
        }
    },

    'cabundle': {
        'args': ['--cabundle'],
        'kwargs': {
            'type': str,
            'help': "Path to CA certificate bundle file"
        }
    },

    'card_slot': {
        'args': ['-c', '--card_slot'],
        'kwargs': {
            'type': str,
            'help': 'The slot number of the card that should be used'
        }
    },

    'certpath': {
        'args': ['--certpath'],
        'kwargs': {
            'type': str,
            'help': "Path to directory containing public keys.  Certificates must end in '.cert'"
        }
    },

    'color': {
        'args': ['--color'],
        'kwargs': {
            'type': str,
            'help': "Disable color or not, accepts true/false"
        }
    },

    'connect': {
        'args': ['--connect'],
        'kwargs': {
            'type': loads,
            'help': "Connection string for the api to retrieve certs"
        }
    },

    'description': {
        'args': ['-d', '--description'],
        'kwargs': {
            'help': "A description of this secret",
            'type': str
        }
    },

    'escrow_users': {
        'args':['-e', '--escrow_users'],
        'kwargs': {
            'help': "Escrow users list is a comma sepearated list of recovery users that each get part of a key",
            'type': str
        },
    },

    'filter': {
        'args': ['-f', '--filter'],
        'kwargs': {
            'help': "Reduce output of commands to matching items",
            'type': str
        },
    },

    'groups': {
        'args': ['-g', '--groups'],
        'kwargs': {
            'type': str,
            'help': 'Comma seperated list of recipient groups'
        }
    },

    'identity': {
        'args': ['-i', '--identity'],
        'kwargs': {
            'type': str,
            'help': 'Override identity of user running the program'
        }
    },

    'ignore_decrypt': {
        'args': ['-I', '--ignore-decrypt'],
        'kwargs': {
            'action': 'store_true',
            'help': 'Ignore decryption errors during show all process'
        }
    },

    'keypath': {
        'args': ['--keypath'],
        'kwargs': {
            'type': str,
            'help': "Path to directory containing private keys.  Keys must end in '.key'"
        }
    },

    'long_escrow':{
        'args': ['-l', '--long-escrow'],
        'kwargs': {
            'action': 'store_true',
            'help': 'Long list passwords that have been escrowed, only shows escrowed passwords'
        }
    },

    'min_escrow': {
        'args': ['-m', '--min_escrow'],
        'kwargs':{
            'type': int,
            'help': "Minimum number of users required to unlock escrowed password"
        }
    },

    'nocache': {
        'args': ['--no-cache'],
        'kwargs': {
            'action': 'store_true',
            'help': 'if using a connector, pull the certs again'
        }
    },

    'noescrow': {
        'args': ['--noescrow'],
        'kwargs':{
            'action': 'store_true',
            'help': 'Do not use escrow functionality, ignore defaults in rc file'
        }
    },

    'nocrypto': {
        'args': ['--nocrypto'],
        'kwargs': {
            'action': 'store_true',
            'help': 'Do not use a password for import/export files'
        }
    },

    'nopassphrase': {
        'args': ['--nopassphrase', '--nopin'],
        'kwargs': {
            'action': 'store_true',
            'help': 'Do not prompt for a pin/passphrase'
        }
    },

    'nosign': {
        'args': ['--nosign'],
        'kwargs': {
            'action': 'store_true',
            'help': 'Do not digitally sign the password information that you are generating'
        }
    },

    'noverify': {
        'args': ['--noverify'],
        'kwargs': {
            'action': 'store_true',
            'help': 'Do not verify certificates and signatures'
        }
    },

    'overwrite': {
        'args': ['--overwrite'],
        'kwargs': {
            'action': 'store_true',
            'help': 'Overwrite a password that already exists'
        }
    },

    'pwfile': {
        'args': ['pwfile'],
        'kwargs': {
            'type': str,
            'help': 'path to the import/export file',
            'nargs': '?',
            'default': None
        }
    },

    'pwname': {
        'args': ['pwname'],
        'kwargs': {
            'type': str,
            'help': 'Name of the password. Ex: passwords/team/infrastructure/root',
            'nargs': '?',
            'default': None
        }
    },

    'pwstore': {
        'args': ['--pwstore', '--srcpwstore'],
        'kwargs': {
            'type': str,
            'help': 'Path to the source password store.  Defaults to "./passwords"'
        }
    },

    'quiet': {
        'args': ['-q', '--quiet'],
        'kwargs': {
            'action': 'store_const',
            'const': -1,
            'default': 0,
            'dest': 'verbosity',
            'help': 'quiet output (show errors only)'
        }
    },

    'recovery': {
        'args': ['-r', '--recovery'],
        'kwargs': {
            'action': 'store_true',
            'help': 'Work with passwords distributed through escrow functionality'
        }
    },

    'rename': {
        'args': ['rename'],
        'kwargs': {
            'type': str,
            'help': 'New name of the password.',
            'nargs': '?',
            'default': None
        }
    },

    'rules' :{
        'args': ['-R', '--rules'],
        'kwargs': {
            'type': str,
            'help': 'Key of rules to use from provided rules map'
        }
    },

    'rules_map' :{
        'args': ['--rules-map'],
        'kwargs': {
            'type': loads,
            'help': 'Map of rules used for automated generation of passwords'
        }
    },

    'stdin': {
        'args': ['--stdin'],
        'kwargs': {
            'action': 'store_true',
            'help': 'Take all password input from stdin instead of from a user input prompt'
        }
    },

    'time': {
        'args': ['-t', '--time'],
        'kwargs': {
            'type': int,
            'help': 'Number of seconds to keep password in paste buffer'
        }
    },

    'theme_map': {
        'args': ['--theme-map'],
        'kwargs': {
            'type': loads,
            'help': 'Map of colors to use for colorized output'
        }
    },
    'type': {
        'args': ['--type'],
        'kwargs': {
            'type': str,
            'help': 'Type of password integration used'
        }
    },

    'users': {
        'args': ['-u', '--users'],
        'kwargs': {
            'type': str,
            'help': 'Comma seperated list of recipients'
        }
    },

    'value': {
        'args': ['--value'],
        'kwargs': {
            'action': 'store_true',
            'help': "Don't update files directly, just dump value onto screen"
        }
    },

    'verbosity': {
        'args': ['-v', '--verbose'],
        'kwargs': {
            'action': 'count',
            'dest': 'verbosity',
            'default': 0,
            'help': 'verbose output (repeat for increased verbosity)'
        }
    }
}

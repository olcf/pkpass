"""This Module defines the arguments that argparse will accept from the CLI"""
import json

ARGUMENTS = {
    ############################################################################
    # Data structure containing all arguments a user could pass into pkpass
    # This helps us de-dupe our work and keep args consistent between
    # subcommands.  We use this with *args and **kwargs constructs
    ############################################################################
    'all': {
        'args': ['-a', '--all'],
        'kwargs': {
            'help': "Show all available password to the given user",
            'action': "store_true"
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

    'connect': {
        'args': ['--connect'],
        'kwargs': {
            'type': json.loads,
            'help': "Connection string for the api to retrieve certs"
        }
    },

    'dstpwstore': {
        'args': ['--dstpwstore'],
        'kwargs': {
            'type': str,
            'help': 'Path to the destination password store.'
        }
    },

    'escrow_users': {
        'args':['-e', '--escrow_users'],
        'kwargs': {
            'help': "Escrow users list is a comma sepearated list of recovery users that each get part of a key",
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

    'noescrow': {
        'args': ['--noescrow'],
        'kwargs':{
            'action': 'store_true',
            'help': 'Do not use escrow functionality, ignore defaults in rc file'
        }
    },

    'nocache': {
        'args': ['--nocache'],
        'kwargs': {
            'action': 'store_true',
            'help': 'Do not use the cached certs for connectors'
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

    'recovery': {
        'args': ['-r', '--recovery'],
        'kwargs': {
            'action': 'store_true',
            'help': 'Work with passwords distributed through escrow functionality'
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

    'users': {
        'args': ['-u', '--users'],
        'kwargs': {
            'type': str,
            'help': 'Comma seperated list of recipients'
        }
    },
}

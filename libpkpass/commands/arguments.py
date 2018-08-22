"""This Module defines the arguments that argparse will accept from the CLI"""
ARGUMENTS = {
    ############################################################################
    # Data structure containing all arguments a user could pass into pkpass
    # This helps us de-dupe our work and keep args consistent between
    # subcommands.  We use this with *args and **kwargs constructs
    ############################################################################

    'pwname': {'args': ['pwname'],
               'kwargs': {'type': str,
                          'help': 'Name of the password. Ex: passwords/team/infrastructure/root',
                          'nargs': '?',
                          'default': None
                         }
              },

    'pwstore': {'args': ['--pwstore, --srcpwstore'],
                'kwargs': {'type': str,
                           'help': 'Path to the source password store.  Defaults to "./passwords"'
                          }
               },

    'dstpwstore': {'args': ['--dstpwstore'],
                   'kwargs': {'type': str,
                              'help': 'Path to the destination password store.'
                             }
                  },

    'identity': {'args': ['-i', '--identity'],
                 'kwargs': {'type': str,
                            'help': 'Override identity of user running the program'
                           }
                },

    'users': {'args': ['-u', '--users'],
              'kwargs': {'type': str,
                         'help': 'Comma seperated list of recipients'
                        }
             },

    'groups': {'args': ['-g', '--groups'],
               'kwargs': {'type': str,
                          'help': 'Comma seperated list of recipient groups'
                         }
              },
    'card_slot': {'args': ['-c', '--card_slot'],
                  'kwargs': {'type': str,
                             'help': 'The slot number of the card that should be used'
                            }
                 },

    'time': {'args': ['-t', '--time'],
             'kwargs': {'type': int,
                        'help': 'Number of seconds to keep password in paste buffer'
                       }
            },

    'overwrite': {'args': ['--overwrite'],
                  'kwargs': {
                      'action': 'store_true',
                      'help': 'Overwrite a password that already exists'
                  }
                 },

    'nopassphrase': {'args': ['--nopassphrase', '--nopin'],
                     'kwargs': {
                         'action': 'store_true',
                         'help': 'Do not prompt for a pin/passphrase'
                     }
                    },

    'noverify': {'args': ['--noverify'],
                 'kwargs': {
                     'action': 'store_true',
                     'help': 'Do not verify certificates and signatures'
                 }
                },

    'nosign': {'args': ['--nosign'],
               'kwargs': {
                   'action': 'store_true',
                   'help': 'Do not digitally sign the password information that you are generating'
               }
              },

    'stdin': {'args': ['--stdin'],
              'kwargs': {
                  'action': 'store_true',
                  'help': 'Take all password input from stdin instead of from a user input prompt'
              }
             },

    'certpath': {'args': ['--certpath'],
                 'kwargs': {
                     'type': str,
                     'help': "Path to directory containing public keys.  Certificates must end in '.cert'"
                 }
                },

    'cabundle': {'args': ['--cabundle'],
                 'kwargs': {
                     'type': str,
                     'help': "Path to CA certificate bundle file"
                 }
                },

    'keypath': {'args': ['--keypath'],
                'kwargs': {
                    'type': str,
                    'help': "Path to directory containing private keys.  Keys must end in '.key'"
                }
               },
    'all': {'args': ['-a', '--all'],
            'kwargs': {
                'help': "Show all available password to the given user",
                'action': "store_true"
            }
           },

}

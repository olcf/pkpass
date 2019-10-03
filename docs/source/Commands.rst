Commands
========
The Commands can be listed out by passing the help flag to pkpass as seen below

.. code-block:: bash


    usage: pkpass.py [-h] [--config CONFIG]
                     {card,clip,create,delete,distribute,export,generate,import,interpreter,list,listrecipients,recover,rename,show,update}
                     ...

    Public Key Password Manager

    positional arguments:
      {card,clip,create,delete,distribute,export,generate,import,interpreter,list,listrecipients,recover,rename,show,update}
                            sub-commands
        card                List the available cards and which card you have
                            selected
        clip                Copy a password to clipboard
        create              Create a new password entry and encrypt it for
                            yourself
        delete              Delete a password in the repository
        distribute          Distribute existing password entry/ies to another
                            entity [matching uses python fnmatch]
        export              Export passwords that you have access to and encrypt
                            with aes
        generate            Generate a new password entry and encrypt it for
                            yourself
        import              Import passwords that you have saved to a file
        interpreter         Interactive mode for pkpass
        list                List passwords you have access to
        listrecipients      List the recipients that pkpass knows about
        recover             Recover a password that has been distributed using
                            escrow functions
        rename              Rename a password in the repository
        show                Display a password
        update              Change a password value and redistribute to recipients

    optional arguments:
      -h, --help            show this help message and exit
      --config CONFIG       Path to a PKPass configuration file. Defaults to
                            '~/.pkpassrc'

Card
----
Card lists out available card slots and the currently chosen one

.. code-block:: bash

    usage: pkpass.py card [-h] [--cabundle CABUNDLE] [--certpath CERTPATH]
                          [-i IDENTITY] [-q] [-v]

    optional arguments:
      -h, --help            show this help message and exit
      --cabundle CABUNDLE   Path to CA certificate bundle file
      --certpath CERTPATH   Path to directory containing public keys. Certificates
                            must end in '.cert'
      -i IDENTITY, --identity IDENTITY
                            Override identity of user running the program
      -q, --quiet           quiet output (show errors only)
      -v, --verbose         verbose output (repeat for increased verbosity)

Clip
----
The intent of clip is to copy a password to your clipboard on the unlock event, currently we are aware of a bug with linux systems

.. code-block:: bash

    usage: pkpass.py clip [-h] [--cabundle CABUNDLE] [-c CARD_SLOT]
                          [--certpath CERTPATH] [-i IDENTITY] [--keypath KEYPATH]
                          [--nopassphrase] [--noverify] [--pwstore PWSTORE] [-q]
                          [--stdin] [-t TIME] [-v]
                          [pwname]

    positional arguments:
      pwname                Name of the password. Ex:
                            passwords/team/infrastructure/root

    optional arguments:
      -h, --help            show this help message and exit
      --cabundle CABUNDLE   Path to CA certificate bundle file
      -c CARD_SLOT, --card_slot CARD_SLOT
                            The slot number of the card that should be used
      --certpath CERTPATH   Path to directory containing public keys. Certificates
                            must end in '.cert'
      -i IDENTITY, --identity IDENTITY
                            Override identity of user running the program
      --keypath KEYPATH     Path to directory containing private keys. Keys must
                            end in '.key'
      --nopassphrase, --nopin
                            Do not prompt for a pin/passphrase
      --noverify            Do not verify certificates and signatures
      --pwstore PWSTORE, --srcpwstore PWSTORE
                            Path to the source password store. Defaults to
                            "./passwords"
      -q, --quiet           quiet output (show errors only)
      --stdin               Take all password input from stdin instead of from a
                            user input prompt
      -t TIME, --time TIME  Number of seconds to keep password in paste buffer
      -v, --verbose         verbose output (repeat for increased verbosity)

Create
------
Create is used to create a password in the configured password repository

.. code-block:: bash

    usage: pkpass.py create [-h] [--cabundle CABUNDLE] [-c CARD_SLOT]
                            [--certpath CERTPATH] [-e ESCROW_USERS] [-i IDENTITY]
                            [--keypath KEYPATH] [-m MIN_ESCROW] [--noescrow]
                            [--nopassphrase] [--nosign] [--overwrite]
                            [--pwstore PWSTORE] [-q] [--stdin] [-v]
                            [pwname]

    positional arguments:
      pwname                Name of the password. Ex:
                            passwords/team/infrastructure/root

    optional arguments:
      -h, --help            show this help message and exit
      --cabundle CABUNDLE   Path to CA certificate bundle file
      -c CARD_SLOT, --card_slot CARD_SLOT
                            The slot number of the card that should be used
      --certpath CERTPATH   Path to directory containing public keys. Certificates
                            must end in '.cert'
      -e ESCROW_USERS, --escrow_users ESCROW_USERS
                            Escrow users list is a comma sepearated list of
                            recovery users that each get part of a key
      -i IDENTITY, --identity IDENTITY
                            Override identity of user running the program
      --keypath KEYPATH     Path to directory containing private keys. Keys must
                            end in '.key'
      -m MIN_ESCROW, --min_escrow MIN_ESCROW
                            Minimum number of users required to unlock escrowed
                            password
      --noescrow            Do not use escrow functionality, ignore defaults in rc
                            file
      --nopassphrase, --nopin
                            Do not prompt for a pin/passphrase
      --nosign              Do not digitally sign the password information that
                            you are generating
      --overwrite           Overwrite a password that already exists
      --pwstore PWSTORE, --srcpwstore PWSTORE
                            Path to the source password store. Defaults to
                            "./passwords"
      -q, --quiet           quiet output (show errors only)
      --stdin               Take all password input from stdin instead of from a
                            user input prompt
      -v, --verbose         verbose output (repeat for increased verbosity)

Delete
------
Delete a password in the repository; pkpass will ask for confirmation. A user could also just remove the file.
This is mostly just to allow testing to be a little faster

.. code-block:: bash

    usage: pkpass.py delete [-h] [--cabundle CABUNDLE] [-c CARD_SLOT]
                            [--certpath CERTPATH] [-i IDENTITY]
                            [--keypath KEYPATH] [--overwrite] [--pwstore PWSTORE]
                            [-q] [--stdin] [-v]
                            [pwname]

    positional arguments:
      pwname                Name of the password. Ex:
                            passwords/team/infrastructure/root

    optional arguments:
      -h, --help            show this help message and exit
      --cabundle CABUNDLE   Path to CA certificate bundle file
      -c CARD_SLOT, --card_slot CARD_SLOT
                            The slot number of the card that should be used
      --certpath CERTPATH   Path to directory containing public keys. Certificates
                            must end in '.cert'
      -i IDENTITY, --identity IDENTITY
                            Override identity of user running the program
      --keypath KEYPATH     Path to directory containing private keys. Keys must
                            end in '.key'
      --overwrite           Overwrite a password that already exists
      --pwstore PWSTORE, --srcpwstore PWSTORE
                            Path to the source password store. Defaults to
                            "./passwords"
      -q, --quiet           quiet output (show errors only)
      --stdin               Take all password input from stdin instead of from a
                            user input prompt
      -v, --verbose         verbose output (repeat for increased verbosity)

Distribute
----------
Distribute takes a pre-existing password in the password repository and grants permission to selected users to be able to unlock it
This function resolves filename matching via python's fnmatch module, depending on the string you may need to pass the value through in single quotes

This function will confirm password list is valid even if only one password matches

.. code-block:: bash

    usage: pkpass.py distribute [-h] [--cabundle CABUNDLE] [-c CARD_SLOT]
                                [--certpath CERTPATH] [-e ESCROW_USERS]
                                [-g GROUPS] [-i IDENTITY] [--keypath KEYPATH]
                                [-m MIN_ESCROW] [--noescrow] [--nopassphrase]
                                [--nosign] [--pwstore PWSTORE] [-q] [--stdin]
                                [-u USERS] [-v]
                                [pwname]

    positional arguments:
      pwname                Name of the password. Ex:
                            passwords/team/infrastructure/root

    optional arguments:
      -h, --help            show this help message and exit
      --cabundle CABUNDLE   Path to CA certificate bundle file
      -c CARD_SLOT, --card_slot CARD_SLOT
                            The slot number of the card that should be used
      --certpath CERTPATH   Path to directory containing public keys. Certificates
                            must end in '.cert'
      -e ESCROW_USERS, --escrow_users ESCROW_USERS
                            Escrow users list is a comma sepearated list of
                            recovery users that each get part of a key
      -g GROUPS, --groups GROUPS
                            Comma seperated list of recipient groups
      -i IDENTITY, --identity IDENTITY
                            Override identity of user running the program
      --keypath KEYPATH     Path to directory containing private keys. Keys must
                            end in '.key'
      -m MIN_ESCROW, --min_escrow MIN_ESCROW
                            Minimum number of users required to unlock escrowed
                            password
      --noescrow            Do not use escrow functionality, ignore defaults in rc
                            file
      --nopassphrase, --nopin
                            Do not prompt for a pin/passphrase
      --nosign              Do not digitally sign the password information that
                            you are generating
      --pwstore PWSTORE, --srcpwstore PWSTORE
                            Path to the source password store. Defaults to
                            "./passwords"
      -q, --quiet           quiet output (show errors only)
      --stdin               Take all password input from stdin instead of from a
                            user input prompt
      -u USERS, --users USERS
                            Comma seperated list of recipients
      -v, --verbose         verbose output (repeat for increased verbosity)

Export
------
Export allows the current user to migrate all his passwords to one file, this tends to be used in conjunction with import

.. code-block:: bash

    usage: pkpass.py export [-h] [--cabundle CABUNDLE] [-c CARD_SLOT]
                            [--certpath CERTPATH] [--dstpwstore DSTPWSTORE]
                            [-i IDENTITY] [--nocrypto] [--nopassphrase] [-q]
                            [--stdin] [-v]
                            [pwfile]

    positional arguments:
      pwfile                path to the import/export file

    optional arguments:
      -h, --help            show this help message and exit
      --cabundle CABUNDLE   Path to CA certificate bundle file
      -c CARD_SLOT, --card_slot CARD_SLOT
                            The slot number of the card that should be used
      --certpath CERTPATH   Path to directory containing public keys. Certificates
                            must end in '.cert'
      --dstpwstore DSTPWSTORE
                            Path to the destination password store.
      -i IDENTITY, --identity IDENTITY
                            Override identity of user running the program
      --nocrypto            Do not use a password for import/export files
      --nopassphrase, --nopin
                            Do not prompt for a pin/passphrase
      -q, --quiet           quiet output (show errors only)
      --stdin               Take all password input from stdin instead of from a
                            user input prompt
      -v, --verbose         verbose output (repeat for increased verbosity)

Generate
--------
Generate allows a user to specify a password name and to have the pkpass system generate it based on a regular expression
an example rules_map could look like the following
rules_map: '{"default": "[^\\s]{20}", "sec": "([a-z]|[A-Z]|[0-9]){15}"}'

.. code-block:: bash

    usage: pkpass.py generate [-h] [--cabundle CABUNDLE] [-c CARD_SLOT]
                              [--certpath CERTPATH] [-e ESCROW_USERS]
                              [-i IDENTITY] [--keypath KEYPATH] [-m MIN_ESCROW]
                              [--noescrow] [--nopassphrase] [--nosign]
                              [--overwrite] [--pwstore PWSTORE] [-q] [-R RULES]
                              [--rules-map RULES_MAP] [--stdin] [-v]
                              [pwname]

    positional arguments:
      pwname                Name of the password. Ex:
                            passwords/team/infrastructure/root

    optional arguments:
      -h, --help            show this help message and exit
      --cabundle CABUNDLE   Path to CA certificate bundle file
      -c CARD_SLOT, --card_slot CARD_SLOT
                            The slot number of the card that should be used
      --certpath CERTPATH   Path to directory containing public keys. Certificates
                            must end in '.cert'
      -e ESCROW_USERS, --escrow_users ESCROW_USERS
                            Escrow users list is a comma sepearated list of
                            recovery users that each get part of a key
      -i IDENTITY, --identity IDENTITY
                            Override identity of user running the program
      --keypath KEYPATH     Path to directory containing private keys. Keys must
                            end in '.key'
      -m MIN_ESCROW, --min_escrow MIN_ESCROW
                            Minimum number of users required to unlock escrowed
                            password
      --noescrow            Do not use escrow functionality, ignore defaults in rc
                            file
      --nopassphrase, --nopin
                            Do not prompt for a pin/passphrase
      --nosign              Do not digitally sign the password information that
                            you are generating
      --overwrite           Overwrite a password that already exists
      --pwstore PWSTORE, --srcpwstore PWSTORE
                            Path to the source password store. Defaults to
                            "./passwords"
      -q, --quiet           quiet output (show errors only)
      -R RULES, --rules RULES
                            Key of rules to use from provided rules map
      --rules-map RULES_MAP
                            Map of rules used for automated generation of
                            passwords
      --stdin               Take all password input from stdin instead of from a
                            user input prompt
      -v, --verbose         verbose output (repeat for increased verbosity)

Import
------
Import allows a user to take an exported password file and import them into a new smart card

.. code-block:: bash

    usage: pkpass.py import [-h] [--cabundle CABUNDLE] [-c CARD_SLOT]
                            [--certpath CERTPATH] [--dstpwstore DSTPWSTORE]
                            [-i IDENTITY] [--nocrypto] [--nopassphrase] [-q]
                            [--stdin] [-v]
                            [pwfile]

    positional arguments:
      pwfile                path to the import/export file

    optional arguments:
      -h, --help            show this help message and exit
      --cabundle CABUNDLE   Path to CA certificate bundle file
      -c CARD_SLOT, --card_slot CARD_SLOT
                            The slot number of the card that should be used
      --certpath CERTPATH   Path to directory containing public keys. Certificates
                            must end in '.cert'
      --dstpwstore DSTPWSTORE
                            Path to the destination password store.
      -i IDENTITY, --identity IDENTITY
                            Override identity of user running the program
      --nocrypto            Do not use a password for import/export files
      --nopassphrase, --nopin
                            Do not prompt for a pin/passphrase
      -q, --quiet           quiet output (show errors only)
      --stdin               Take all password input from stdin instead of from a
                            user input prompt
      -v, --verbose         verbose output (repeat for increased verbosity)

Interpreter
-----------
Creates an interactive session, the default behavior of pkpass if no arguments are passed

.. code-block:: bash

    usage: pkpass.py interpreter [-h] [--cabundle CABUNDLE] [-c CARD_SLOT]
                                 [--certpath CERTPATH] [--connect CONNECT]
                                 [-e ESCROW_USERS] [-g GROUPS] [-i IDENTITY]
                                 [--keypath KEYPATH] [-m MIN_ESCROW]
                                 [--pwstore PWSTORE] [-q] [-v]

    optional arguments:
      -h, --help            show this help message and exit
      --cabundle CABUNDLE   Path to CA certificate bundle file
      -c CARD_SLOT, --card_slot CARD_SLOT
                            The slot number of the card that should be used
      --certpath CERTPATH   Path to directory containing public keys. Certificates
                            must end in '.cert'
      --connect CONNECT     Connection string for the api to retrieve certs
      -e ESCROW_USERS, --escrow_users ESCROW_USERS
                            Escrow users list is a comma sepearated list of
                            recovery users that each get part of a key
      -g GROUPS, --groups GROUPS
                            Comma seperated list of recipient groups
      -i IDENTITY, --identity IDENTITY
                            Override identity of user running the program
      --keypath KEYPATH     Path to directory containing private keys. Keys must
                            end in '.key'
      -m MIN_ESCROW, --min_escrow MIN_ESCROW
                            Minimum number of users required to unlock escrowed
                            password
      --pwstore PWSTORE, --srcpwstore PWSTORE
                            Path to the source password store. Defaults to
                            "./passwords"
      -q, --quiet           quiet output (show errors only)
      -v, --verbose         verbose output (repeat for increased verbosity)

List
----
List shows all passwords available to a given user

.. code-block:: bash

    usage: pkpass.py list [-h] [--cabundle CABUNDLE] [--certpath CERTPATH]
                          [-f FILTER] [-i IDENTITY] [--pwstore PWSTORE] [-q] [-r]
                          [--stdin] [-v]

    optional arguments:
      -h, --help            show this help message and exit
      --cabundle CABUNDLE   Path to CA certificate bundle file
      --certpath CERTPATH   Path to directory containing public keys. Certificates
                            must end in '.cert'
      -f FILTER, --filter FILTER
                            Reduce output of commands to matching items
      -i IDENTITY, --identity IDENTITY
                            Override identity of user running the program
      --pwstore PWSTORE, --srcpwstore PWSTORE
                            Path to the source password store. Defaults to
                            "./passwords"
      -q, --quiet           quiet output (show errors only)
      -r, --recovery        Work with passwords distributed through escrow
                            functionality
      --stdin               Take all password input from stdin instead of from a
                            user input prompt
      -v, --verbose         verbose output (repeat for increased verbosity)

Listrecipients
--------------
List the recipients that pkpass knows about

.. code-block:: bash

    usage: pkpass.py listrecipients [-h] [--cabundle CABUNDLE]
                                    [--certpath CERTPATH] [-f FILTER]
                                    [-i IDENTITY] [-q] [--stdin] [-v]

    optional arguments:
      -h, --help            show this help message and exit
      --cabundle CABUNDLE   Path to CA certificate bundle file
      --certpath CERTPATH   Path to directory containing public keys. Certificates
                            must end in '.cert'
      -f FILTER, --filter FILTER
                            Reduce output of commands to matching items
      -i IDENTITY, --identity IDENTITY
                            Override identity of user running the program
      -q, --quiet           quiet output (show errors only)
      --stdin               Take all password input from stdin instead of from a
                            user input prompt
      -v, --verbose         verbose output (repeat for increased verbosity)

Recover
-------
Recover serves the purpose of recovering escrowed passwords in the event no one in the distributed list can properly unlock a password.
This requires password owners to have created escrow users. Each necessary escrow user will place his share into the program.

.. code-block:: bash

    usage: pkpass.py recover [-h] [--cabundle CABUNDLE] [--certpath CERTPATH]
                             [-e ESCROW_USERS] [-i IDENTITY] [--keypath KEYPATH]
                             [-m MIN_ESCROW] [--nosign] [--pwstore PWSTORE] [-q]
                             [-v]

    optional arguments:
      -h, --help            show this help message and exit
      --cabundle CABUNDLE   Path to CA certificate bundle file
      --certpath CERTPATH   Path to directory containing public keys. Certificates
                            must end in '.cert'
      -e ESCROW_USERS, --escrow_users ESCROW_USERS
                            Escrow users list is a comma sepearated list of
                            recovery users that each get part of a key
      -i IDENTITY, --identity IDENTITY
                            Override identity of user running the program
      --keypath KEYPATH     Path to directory containing private keys. Keys must
                            end in '.key'
      -m MIN_ESCROW, --min_escrow MIN_ESCROW
                            Minimum number of users required to unlock escrowed
                            password
      --nosign              Do not digitally sign the password information that
                            you are generating
      --pwstore PWSTORE, --srcpwstore PWSTORE
                            Path to the source password store. Defaults to
                            "./passwords"
      -q, --quiet           quiet output (show errors only)
      -v, --verbose         verbose output (repeat for increased verbosity)

Rename
------
This renames a password in the given repository

.. code-block:: bash

    usage: pkpass.py rename [-h] [--cabundle CABUNDLE] [-c CARD_SLOT]
                            [--certpath CERTPATH] [-i IDENTITY]
                            [--keypath KEYPATH] [--nopassphrase] [--overwrite]
                            [--pwstore PWSTORE] [-q] [--stdin] [-v]
                            [pwname] [rename]

    positional arguments:
      pwname                Name of the password. Ex:
                            passwords/team/infrastructure/root
      rename                New name of the password.

    optional arguments:
      -h, --help            show this help message and exit
      --cabundle CABUNDLE   Path to CA certificate bundle file
      -c CARD_SLOT, --card_slot CARD_SLOT
                            The slot number of the card that should be used
      --certpath CERTPATH   Path to directory containing public keys. Certificates
                            must end in '.cert'
      -i IDENTITY, --identity IDENTITY
                            Override identity of user running the program
      --keypath KEYPATH     Path to directory containing private keys. Keys must
                            end in '.key'
      --nopassphrase, --nopin
                            Do not prompt for a pin/passphrase
      --overwrite           Overwrite a password that already exists
      --pwstore PWSTORE, --srcpwstore PWSTORE
                            Path to the source password store. Defaults to
                            "./passwords"
      -q, --quiet           quiet output (show errors only)
      --stdin               Take all password input from stdin instead of from a
                            user input prompt
      -v, --verbose         verbose output (repeat for increased verbosity)

Show
----
This unlocks a password and displays it on stdout

.. code-block:: bash

    usage: pkpass.py show [-h] [-a] [--cabundle CABUNDLE] [-c CARD_SLOT]
                          [--certpath CERTPATH] [-i IDENTITY] [-I]
                          [--keypath KEYPATH] [--nopassphrase] [--noverify]
                          [--pwstore PWSTORE] [-q] [-r] [--stdin] [-v]
                          [pwname]

    positional arguments:
      pwname                Name of the password. Ex:
                            passwords/team/infrastructure/root

    optional arguments:
      -h, --help            show this help message and exit
      -a, --all             Show all available password to the given user, if a
                            pwname is supplied filtering will be done case-
                            insensitivey based on the filename
      --cabundle CABUNDLE   Path to CA certificate bundle file
      -c CARD_SLOT, --card_slot CARD_SLOT
                            The slot number of the card that should be used
      --certpath CERTPATH   Path to directory containing public keys. Certificates
                            must end in '.cert'
      -i IDENTITY, --identity IDENTITY
                            Override identity of user running the program
      -I, --ignore-decrypt  Ignore decryption errors during show all process
      --keypath KEYPATH     Path to directory containing private keys. Keys must
                            end in '.key'
      --nopassphrase, --nopin
                            Do not prompt for a pin/passphrase
      --noverify            Do not verify certificates and signatures
      --pwstore PWSTORE, --srcpwstore PWSTORE
                            Path to the source password store. Defaults to
                            "./passwords"
      -q, --quiet           quiet output (show errors only)
      -r, --recovery        Work with passwords distributed through escrow
                            functionality
      --stdin               Take all password input from stdin instead of from a
                            user input prompt
      -v, --verbose         verbose output (repeat for increased verbosity)

Update
------
This changes a password value and redistributes the password to the recipients

.. code-block:: bash

    usage: pkpass.py update [-h] [--cabundle CABUNDLE] [-c CARD_SLOT]
                            [--certpath CERTPATH] [-e ESCROW_USERS] [-i IDENTITY]
                            [--keypath KEYPATH] [-m MIN_ESCROW] [--noescrow]
                            [--nopassphrase] [--nosign] [--overwrite]
                            [--pwstore PWSTORE] [-q] [--stdin] [-v]
                            [pwname]

    positional arguments:
      pwname                Name of the password. Ex:
                            passwords/team/infrastructure/root

    optional arguments:
      -h, --help            show this help message and exit
      --cabundle CABUNDLE   Path to CA certificate bundle file
      -c CARD_SLOT, --card_slot CARD_SLOT
                            The slot number of the card that should be used
      --certpath CERTPATH   Path to directory containing public keys. Certificates
                            must end in '.cert'
      -e ESCROW_USERS, --escrow_users ESCROW_USERS
                            Escrow users list is a comma sepearated list of
                            recovery users that each get part of a key
      -i IDENTITY, --identity IDENTITY
                            Override identity of user running the program
      --keypath KEYPATH     Path to directory containing private keys. Keys must
                            end in '.key'
      -m MIN_ESCROW, --min_escrow MIN_ESCROW
                            Minimum number of users required to unlock escrowed
                            password
      --noescrow            Do not use escrow functionality, ignore defaults in rc
                            file
      --nopassphrase, --nopin
                            Do not prompt for a pin/passphrase
      --nosign              Do not digitally sign the password information that
                            you are generating
      --overwrite           Overwrite a password that already exists
      --pwstore PWSTORE, --srcpwstore PWSTORE
                            Path to the source password store. Defaults to
                            "./passwords"
      -q, --quiet           quiet output (show errors only)
      --stdin               Take all password input from stdin instead of from a
                            user input prompt
      -v, --verbose         verbose output (repeat for increased verbosity)

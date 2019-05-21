Commands
========
The Commands can be listed out by passing the help flag to pkpass as seen below

.. code-block:: bash

    python pkpass.py -h
    usage: pkpass.py [-h] [--config CONFIG]
                     {clip,create,distribute,export,import,list,listrecipients,recover,show}
                     ...
    
    Public Key Password Manager
    
    positional arguments:
      {clip,create,distribute,export,import,list,listrecipients,recover,show}
                            sub-commands
        clip                Copy a password to clipboard
        create              Create a new password entry and encrypt it for
                            yourself
        distribute          Distribute an existing password entry to another
                            entity
        export              Export passwords that you have access to and encrypt
                            with aes
        import              Import passwords that you have saved to a file
        list                List passwords you have access to
        listrecipients      List the recipients that pkpass knows about
        recover             Recover a password that has been distributed using
                            escrow functions
        show                Display a password
    
    optional arguments:
      -h, --help            show this help message and exit
      --config CONFIG       Path to a PKPass configuration file. Defaults to
                            '~/.pkpassrc'

Clip
----
The intent of clip is to copy a password to your clipboard on the unlock event, currently we are aware of a bug with linux systems

.. code-block:: bash

    usage: pkpass.py clip [-h] [--cabundle CABUNDLE] [-c CARD_SLOT]
                          [--certpath CERTPATH] [-i IDENTITY] [--keypath KEYPATH]
                          [--nocache] [--nopassphrase] [--noverify]
                          [--pwstore PWSTORE] [--stdin] [-t TIME]
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
      --nocache             Do not use the cached certs for connectors
      --nopassphrase, --nopin
                            Do not prompt for a pin/passphrase
      --noverify            Do not verify certificates and signatures
      --pwstore PWSTORE, --srcpwstore PWSTORE
                            Path to the source password store. Defaults to
                            "./passwords"
      --stdin               Take all password input from stdin instead of from a
                            user input prompt
      -t TIME, --time TIME  Number of seconds to keep password in paste buffer

Create
------
Create is used to create a password in the configured password repository

.. code-block:: bash

    usage: pkpass.py create [-h] [--cabundle CABUNDLE] [-c CARD_SLOT]
                            [--certpath CERTPATH] [-e ESCROW_USERS] [-i IDENTITY]
                            [--keypath KEYPATH] [-m MIN_ESCROW] [--noescrow]
                            [--nopassphrase] [--nosign] [--noverify] [--overwrite]
                            [--pwstore PWSTORE] [--stdin]
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
      --noverify            Do not verify certificates and signatures
      --overwrite           Overwrite a password that already exists
      --pwstore PWSTORE, --srcpwstore PWSTORE
                            Path to the source password store. Defaults to
                            "./passwords"
      --stdin               Take all password input from stdin instead of from a
                            user input prompt
    
Distribute
----------
Distribute takes a pre-existing password in the password repository and grants permission to selected users to be able to unlock it

.. code-block:: bash

    usage: pkpass.py distribute [-h] [--cabundle CABUNDLE] [-c CARD_SLOT]
                                [--certpath CERTPATH] [-e ESCROW_USERS]
                                [-g GROUPS] [-i IDENTITY] [--keypath KEYPATH]
                                [-m MIN_ESCROW] [--noescrow] [--nopassphrase]
                                [--nosign] [--noverify] [--pwstore PWSTORE]
                                [--stdin] [-u USERS]
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
      --noverify            Do not verify certificates and signatures
      --pwstore PWSTORE, --srcpwstore PWSTORE
                            Path to the source password store. Defaults to
                            "./passwords"
      --stdin               Take all password input from stdin instead of from a
                            user input prompt
      -u USERS, --users USERS
                            Comma seperated list of recipients

Export
------
Export allows the current user to migrate all his passwords to one file, this tends to be used in conjunction with import

.. code-block:: bash

    usage: pkpass.py export [-h] [--cabundle CABUNDLE] [-c CARD_SLOT]
                            [--certpath CERTPATH] [--dstpwstore DSTPWSTORE]
                            [-i IDENTITY] [--nocrypto] [--nopassphrase]
                            [--noverify] [--stdin]
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
      --noverify            Do not verify certificates and signatures
      --stdin               Take all password input from stdin instead of from a
                            user input prompt
    
Import
------
Import allows a user to take an exported password file and import them into a new smart card

.. code-block:: bash

    usage: pkpass.py import [-h] [--cabundle CABUNDLE] [-c CARD_SLOT]
                            [--certpath CERTPATH] [--dstpwstore DSTPWSTORE]
                            [-i IDENTITY] [--nocrypto] [--nopassphrase]
                            [--noverify] [--stdin]
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
      --noverify            Do not verify certificates and signatures
      --stdin               Take all password input from stdin instead of from a
                            user input prompt
    
List
----
List shows all passwords available to a given user

.. code-block:: bash

    usage: pkpass.py list [-h] [--cabundle CABUNDLE] [--certpath CERTPATH]
                          [-i IDENTITY] [--nocache] [--noverify]
                          [--pwstore PWSTORE] [-r] [--stdin]
    
    optional arguments:
      -h, --help            show this help message and exit
      --cabundle CABUNDLE   Path to CA certificate bundle file
      --certpath CERTPATH   Path to directory containing public keys. Certificates
                            must end in '.cert'
      -i IDENTITY, --identity IDENTITY
                            Override identity of user running the program
      --nocache             Do not use the cached certs for connectors
      --noverify            Do not verify certificates and signatures
      --pwstore PWSTORE, --srcpwstore PWSTORE
                            Path to the source password store. Defaults to
                            "./passwords"
      -r, --recovery        Work with passwords distributed through escrow
                            functionality
      --stdin               Take all password input from stdin instead of from a
                            user input prompt
    

listrecipients
--------------
List the recipients that pkpass knows about

.. code-block:: bash

    usage: pkpass.py listrecipients [-h] [--cabundle CABUNDLE]
                                    [--certpath CERTPATH] [-i IDENTITY]
                                    [--noverify] [--stdin]
    
    optional arguments:
      -h, --help            show this help message and exit
      --cabundle CABUNDLE   Path to CA certificate bundle file
      --certpath CERTPATH   Path to directory containing public keys. Certificates
                            must end in '.cert'
      -i IDENTITY, --identity IDENTITY
                            Override identity of user running the program
      --noverify            Do not verify certificates and signatures
      --stdin               Take all password input from stdin instead of from a
                            user input prompt
    
recover
-------
Recover serves the purpose of recovering escrowed passwords in the event no one in the distributed list can properly unlock a password.
This requires password owners to have created escrow users. Each necessary escrow user will place his share into the program.

.. code-block:: bash

    usage: pkpass.py recover [-h] [--cabundle CABUNDLE] [--certpath CERTPATH]
                             [-e ESCROW_USERS] [-i IDENTITY] [--keypath KEYPATH]
                             [-m MIN_ESCROW] [--nosign] [--noverify]
                             [--pwstore PWSTORE]
    
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
      --noverify            Do not verify certificates and signatures
      --pwstore PWSTORE, --srcpwstore PWSTORE
                            Path to the source password store. Defaults to
                            "./passwords"
    
show
----
This unlocks a password and displays it on stdout

.. code-block:: bash

    usage: pkpass.py show [-h] [-a] [--cabundle CABUNDLE] [-c CARD_SLOT]
                          [--certpath CERTPATH] [-i IDENTITY] [-I]
                          [--keypath KEYPATH] [--nocache] [--nopassphrase]
                          [--noverify] [--pwstore PWSTORE] [-r] [--stdin]
                          [pwname]

    
    positional arguments:
      pwname                Name of the password. Ex:
                            passwords/team/infrastructure/root
    
    optional arguments:
      -h, --help            show this help message and exit
      -a, --all             Show all available password to the given user
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
      --nocache             Do not use the cached certs for connectors
      --nopassphrase, --nopin
                            Do not prompt for a pin/passphrase
      --noverify            Do not verify certificates and signatures
      --pwstore PWSTORE, --srcpwstore PWSTORE
                            Path to the source password store. Defaults to
                            "./passwords"
      -r, --recovery        Work with passwords distributed through escrow
                            functionality
      --stdin               Take all password input from stdin instead of from a
                            user input prompt
    

Configuration
=============

Password Repository
-------------------
Passwords are created on the file system, so any destination may be specified.  For passwords that need to be distributed to other users, convention suggests putting these into a hierarchy with the root in 'passwords'.  To make the repository as flat as possible, the top level will contain mostly groupings of passwords, with the next level containing the passwords themselves.  
Examples of groups may include "security-team", "database-users", "passwords/general", etc.  It is up to each organization to determine the best hierarchy for storing passwords.  The 'list' command and 'showall' commands will crawl the hierarchy starting at the root regardless of structure.

You may distribute passwords to a specified group defined in your pkpassrc file. These groups may be arbitrary

.. code-block:: bash

    databaseadmins: db1, db2,db3
    secadmins: admin1,  admin2 ,  admin3
    groups: secadmins, databaseadmins

you may also specify on the command line which groups to use: ``pkpass.py distribute password -g secadmins``

Cert Repository
---------------
Certs are read into PkPass and are used in many of the processes. This can be presented to pkpass as a directory structure, repository, or
by means of it's ``connector`` functionality. 

CA Bundle
---------
The CA bundle is used to verify valid certs

Arguments
---------
The RC file can take the majority of PkPass's arguments so that you do not need to pass them through. The only ones that should not be relied upon to work properly
are arguments with 'store_true' or 'store_false' attributes. The following arguments should work in a pkpassrc file

.. code-block:: bash

    cabundle
    card_slot
    certpath
    color
    connect
    escrow_users
    groups
    identity
    keypath
    min_escrow
    pwstore
    rules
    rules_map
    theme_map
    time
    users

These along with user-defined groups should all work in an RC file.

Special Treatment for Non-piv accounts/credentials
--------------------------------------------------
There are some capabilities built into pkpass.py to manage passwords with rsa keys and x509 certificates without using smart card authentication.  These
keys still need to be signed by a CA in the CA bundle.
Create a keypair:

This will create an unsigned keypair.  We really want it to create a certificate request in the future

.. code-block:: bash

    openssl req -newkey rsa:4096 -keyout local.key -x509 -out local.cert

As long as the private and public keys are in directories that pkpass can find, distribution to those identities works exactly the same.  Keys must be named 'username.key'.  For user foo, the private key must be named 'foo.key' and reside in the keypath directory.

Behalf of functionality
-----------------------
To utilize the functionality for showing a password on behalf of another user you need to create a password that is the private key of this user. Then when you issue a show command you specify the username with the `-b` flag

Example:

.. code-block:: bash

    pkpass show password_i_dont_have_direct_access_to -b rsa_user

the argument `rsa_user` needs to be both the username and the password name for the password that store's this user's rsa key

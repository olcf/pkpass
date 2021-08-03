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
The RC file (location ~/.pkpassrc, ~/.pkpassrc.yaml, or ~/.pkpassrc.yml) can take the majority of PkPass's arguments so that you do not need to pass them through. The only ones that should not be relied upon to work properly
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

Populate other data stores
--------------------------
Currently Pkpass can populate puppet-eyaml given appropriate configurations:

It is suggested to have a `~/.eyaml/config.yaml` setup with `pkcs7_public_key:` defined at the highest level of that file.

To completely configure this integration on the pkpass side please add values to your rc file that looks similar to the following

.. code-block:: yaml

    populate:
      # puppet_eyaml is the definition for the `type`
      puppet_eyaml:
        # `bin` is the location of the binary for `eyaml`
        bin: /opt/puppetlabs/pdk/share/cache/ruby/2.5.0/bin/eyaml
        # `directory` is the directory of your puppet repo
        directory: ~/git/puppet
        passwords:
          # This level entry (`ops/password`) represents a pkpass password name
          ops/password:
            # This level entry (`data/team/security.yaml`) represents the rest of the file path for the heira file
            data/team/security.yaml:
              # The following list represents the keys that need to be replaced in the heira file
              - some::server::password
              - some:other::server


To populate kubernetes you need a similar block
Currently pkpass can only generate a single encrypted value per secret. It places the value stored in pkpass in the map where it's name is matched.

in the following example you will see this, so for `testpass` pkpass will decrypt `testpass` and place the value of that password in `data/password` because in the configuration file the value of `data/password` is `testpass`

Pkpass will then base64 encode all values in the `data` map and dump it as a yaml file in where `output` is defined, in this case `/tmp/secrets.yaml`

.. code-block:: yaml

    populate:
      kubernetes:
        output: /tmp/secrets.yaml
        passwords:
          testpass:
            - apiVersion: v1
              type: Opaque
              metadata:
                name: test
                namespace: testing
              data:
                password: testpass
                username: someuser
            - apiVersion: v1
              type: Opaque
              metadata:
                name: test
                namespace: testing2
              data:
                password: testpass
                username: someuser


It is not recommended to store the kubernetes output file anywhere, since kubernetes secrets are just base64 encoded, they are not secure!

other data endpoints may be requested

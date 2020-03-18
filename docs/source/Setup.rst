Setup
=====
Pip install is available via:
  | ``pip install pkpass-olcf``

Brew install is available via:
  | ``brew install olcf/tap/pkpass``

You may clone the pkpass.py tool like this:
  | ``git clone https://github.com/olcf/pkpass.git``

If you are using additional PIV/X509 certificate repositories or password repositories, you will need to create local directories for them, or create repositories in a git server that you have access to.  Note that while the passwords are safely encrypted and can be distributed without fear of
compromise, there may be other information such as system names, account names, and personnel information that you do not want to be publicly available.


RC file
-------
Pkpass has an RC file that can store default values for you so you don't have to write an essay everytime you want to look at or create passwords.

An example file is below

.. code-block:: bash

    certpath: /Users/username/passdb/certs/  
    keypath: /Users/username/passdb/keys/  
    cabundle: /Users/username/passdb/cabundles/ca.bundle  
    pwstore: /Users/username/passdb/passwords/  

In this case, 'passdb' is the name of the directory in the user's home area that contains x509 certificates, keys (if necessary) and the ca bundle.

The RC file can store any command line argument that is not a true/false value. See Configuration for more details


CA Bundle
---------
You can create a ca bundle by combining all CA Certificates that you trust into one file and moving the file to the cabundle path.  Usually the site admins create this CA Bundle for users as part of their certificate management practices.  
Example

.. code-block:: bash

    cd "${directory_with_ca_certs}"
    cat * > ca.bundle
    cp ca.bundle "${cabundle_path_in_rc_file}"

Additionally, note that most options you can pass on the command line may be passed in through the .pkpassrc file as well.
true/false options however (such as --noverify or --nocache), cannot at this time be passed into the command like

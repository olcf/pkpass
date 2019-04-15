Setup
=====

You may clone the pkpass.py tool like this:
  | ``git clone https://github.com/olcf/pkpass.git``

If you are using additional PIV/X509 certificate repositories or password repositories, you will need to create local directories for them, or create repositories in a git server that you have access to.  Note that while the passwords are safely encrypted and can be distributed without fear of
compromise, there may be other information such as system names, account names, and personnel information that you do not want to be publicly available.



Setup/Initial
-------------
For the initial setup there are two scripts that you can run, each can serve the same function.
The bash script ``./setup.sh`` obviously will only work on systems with bash such as linux and macos
The python script ``./setup.py`` *should* run on all systems.

* bash:  
    This script will walk you through a full installation including setting up venvs if you need that.  

* python:  
    | This will run through specific commands  
    | ``python setup.py rcfile`` will create an rcfile  
    | ``python setup.py install`` will run the installation on a system level  
    | ``python setup.py install --user`` will run the installation on a user level  
    | ``python setup.py verify -r "/path/to/.pkpassrc"`` will do basic linting of the pkpassrc file
    | if you need the -h flag may help.  

In both cases, these files can install dependencies and create a .pkpassrc file for you

If you would like to proceed manually, or have problems with the setup script:
You will want to create a .pkpassrc file in your home directory.  A typical pkpassrc file looks like this:

.. code-block:: bash

    certpath: /Users/username/passdb/certs/  
    keypath: /Users/username/passdb/keys/  
    cabundle: /Users/username/passdb/cabundles/ca.bundle  
    pwstore: /Users/username/passdb/passwords/  

In this case, 'passdb' is the name of the directory in the user's home area that contains x509 certificates, keys (if necessary) and the ca bundle.

You can create a ca bundle by combining all CA Certificates that you trust into one file and moving the file to the cabundle path.  Usually the site admins create this CA Bundle for users as part of their certificate management practices.  
Example

.. code-block:: bash

    cd "${directory_with_ca_certs}"
    cat * > ca.bundle
    cp ca.bundle "${cabundle_path_in_rc_file}"

Additionally, note that most options you can pass on the command line may be passed in through the .pkpassrc file as well.
true/false options however (such as --noverify or --nocache), cannot at this time be passed into the command like

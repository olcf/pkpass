PKPass: Public Key Based Password Manager
=============

Overview
--------
This is a basic password store and password manager for maintaining arbitrary secrets.

The password management solution provides:

  - Encryption at Rest
  - Password distribution/organization based on definable hierarchies
  - Password creation timestamps
  - Password history and change logs
  - Distributed backup capabilities
  - PIV/Smartcard Credential encryption/decryption
  - Import and export functionality (WIP)

Passwords that are created are distributed to recipients by public key encryption.  The x509 certificate of the intended recipient is used to create an encrypted copy of the distributed password that is then saved in a password-specific git repository.  Multiple encrypted copies of the secret are created, one for each user.  End users then check out the git repo and are able to read passwords using their PIV/Smartcard credential to decrypt.


x509 Certificate Repository
-------
PKPass needs a trusted x509 certificate repository, which typically is managed using git.  Certificates in this repository should all be
signed by Certificate Authorities that can be found in the CABundle file that PKPass is configured to look at.  Since this repository should be
considered 'trusted', it is typically managed by a smaller trusted set of site administrators.  PKPass validates all encryption certificates as they are used to make sure they are signed by a trusted Certificate Authority (CA).


You may also use a local x509 certificate repository that you sync with others using RSYNC, NFS, shared volumes, etc.  You can configure the directory that pkpass will use for the certificate repository either on the command line, or through the .pkpassrc file.

The CABundle file to use can also be configured in the .pkpassrc file or on the command line.

Additionally, certificates should be named <username>.cert.  For example, the certificate for user 'jason' should be named 'jason.cert' inside this x509 directory.


Password Repository
--------
PKPass also needs a directory to serve as a 'password database'.  Like the x509 certificate repository, it is also typically managed with git to provide change control, history, and tracking of changes.  Local directories can also be used and shared via rsync, NFS, shared volumes, etc if preferred.

To change the default password repository, you may specify another directory on the command line or in the .pkpassrc file.


Using the tool
========

Setup/Cloning
-----------

You may clone the pkpass.py tool like this:
  - `git clone https://github.com/olcf/pkpass.git`

If you are using additional PIV/X509 certificate repositories or password repositories, you will need to create local directories for them, or create repositories in a git server that you have access to.  Note that while the passwords are safely encrypted and can be distributed without fear of
compromise, there may be other information such as system names, account names, and personnel information that you do not want to be publicly available.



Setup/Initial
-----------

For inital setup you may want to run the provided setup script at the root of the project
`./setup.sh`
This interactive setup script will install dependencies and create a .pkpassrc file for you

If you would like to proceed manually, or have problems with the setup script:
You will want to create a .pkpassrc file in the pkpass repository that you have cloned.  A typical pkpassrc file looks like this:


  certpath: /Users/username/passdb/certs/  
  keypath: /Users/username/passdb/keys/  
  cabundle: /Users/username/passdb/cabundles/ca.bundle  
  pwstore: /Users/username/passdb/passwords/  


In this case, 'passdb' is the name of the directory in the user's home area that contains x509 certificates, keys (if necessary) and the ca bundle.

You can create a ca bundle by combining all CA Certificates that you trust into one file and moving the file to the cabundle path.  Usually the site admins create this CA Bundle for users as part of their certificate management practices.

Additionally, note that arguments you can pass on the command line may be passed in through the .pkpassrc file as well.

Command Overview
----------------

```
  $ ./pkpass.py --help
  usage: pkpass.py [-h] [--config CONFIG]
                 {create,distribute,show,clip,list,listrecipients,export} ...

  Public Key Password Manager

  positional arguments:
  {create,distribute,show,clip,list,listrecipients,export}
                        sub-commands
    create              Create a new password entry and encrypt it for
                        yourself
    distribute          Distribute an existing password entry to another
                        entity
    show                Display a password
    clip                Copy a password to clipboard
    list                List passwords you have access to
    listrecipients      List the recipients that pkpass knows about
    export              Export passwords that you have access to and encrypt
                        with aes

  optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       Path to a PKPass configuration file. Defaults to
                        '.pkpassrc'
```


General Usage
----------
Run ./pkpass.py with the '-h' flag for a list of options as well as syntax.  Some common usage examples follow:
  - Create a new security team root password in the password store:
    * `./pkpass.py create security-team/rootpw`

  - Distribute the security team root password to other team members 'foo' and 'bar':
    * `./pkpass.py distribute -u foo,bar security-team/rootpw`

  - List the names of all passwords that have been distributed to you:
    * `./pkpass.py list`

  - Show the infrastructure team root password:
    * `./pkpass.py show infra-team/rootpw`

  - Show all the passwords that you know:
    * `./pkpass.py show -a`

  - List the names of all passwords that have been distributed to user identity 'foo':
    * `./pkpass.py list -i foo`

  - Show the users that pkpass detects certificates for in the certificate repository:
    * `./pkpass.py listrecipients`


Configuring the Tool
===================


Password Repository
-------------------

Passwords are created on the file system, so any destination may be specified.  For passwords that need to be distributed to other users, convention suggests putting these into a hierarchy with the root in 'passwords'.  To make the repository as flat as possible, the top level will contain mostly groupings of passwords, with the next level containing the passwords themselves.  Examples of groups may include "security-team", "database-users", "passwords/general", etc.  It is up to each organization to determine the best hierarchy for storing passwords.  The 'list' command and 'showall' commands will crawl the hierarchy starting at the root regardless of structure.

Special Treatment for Non-piv accounts/credentials
====================
There are some capabilities built into pkpass.py to manage passwords with rsa keys and x509 certificates without using smart card authentication.  These
keys still need to be signed by a CA in the CA bundle.  Basic usage:


Create a keypair
----------------
This will create an unsigned keypair.  We really want it to create a certificate request in the future
`openssl req -newkey rsa:4096 -keyout local.key -x509 -out local.crt`

As long as the private and public keys are in directories that pkpass can find, distribution to those identities works exactly the same.  Keys must be named 'username.key'.  For user foo, the private key must be named 'foo.key' and reside in the keypath directory.


Import/Export Passwords to/from file: formatting considerations
====================
__Work In Progress__  
Pkpass's import and export function utilizes a file to pull passwords from or put passwords in. This can be particularly useful for backing up your passwords or when you are switching smartcards.

The import file should contain one entry per line, with the password name and value separated by `<COLON><TAB>`. For example:

```
# ImportOldPasswords.txt
./passwords/security-team/testPassName:	ThisIsYourPassword
./passwords/security-team/otherpassword:	YetAnotherPassword
```

Export Passwords: Security Considerations
====================
__Work In Progress__
Pkpass supports automatic encryption of passwords while utilizing password export. This is the recomended use of Pkpass. Ex:
  `./pkpass export ~/exportFile`

You can then subsequntly import the cipher text using the import function:
  `./pkpass import ~/exportFile`

Please remember to use good password practices with this file.


If you so choose, you can export to a plaintext file using the `--nocrypto` flag. This method is not recommended for security purposes:  
  `./pkpass export --nocrypto ~/exportFile`


Software Dependencies
====================
Pkpass has few dependencies. Fernet is a crypto library used to allow automatic symmetric encrypting.  Fernet can be installed using pip:
  pip install cryptography

Other dependencies can be found in requirements.txt  
__Note:__ All dependencies will be installed if the setup script is run.

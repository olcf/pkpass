PKPass: Public Key Based Password Manager
=============

![Python package](https://github.com/olcf/pkpass/workflows/Python%20package/badge.svg)

RTD
===
https://pkpass.readthedocs.io/en/latest/


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
  - Import and export functionality

Passwords that are created are distributed to recipients by public key encryption.  The x509 certificate of the intended recipient is used to create an encrypted copy of the distributed password that is then saved in a password-specific git repository.  Multiple encrypted copies of the secret are created, one for each user.  End users then check out the git repo and are able to read passwords using their PIV/Smartcard credential to decrypt.

Install
-------

### Everything:
`pip install pkpass-olcf`

### MacOs:
`brew install olcf/tap/pkpass`


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

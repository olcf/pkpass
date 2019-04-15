Development and Testing
======================

Testing Scripts
-----------------
Currently there exists a shell script `./test/pki/generatepki.sh` that will generate certificates for a developer to use for unittests
After running this script, you can run tox or the `./unittest.sh` file; note that `./unittest.sh` does not test multiple versions of
python like tox does

Plugin Behavior - Connectors
---------------
We currently support dropping arbitary connection plugins into `./libpkpass/connectors` the connectors should return
certificates, example usage here is if your organization stores certs in a custom web application, or in ldap or
the like, you can create a connector to interface with that and feed pkpass certs in this manner

Connectors will be ignored due to the gitignore, I recommend creating a separate repo for that purpose. To use
a connector pkpass needs a `connect` argument

`
connect: '{"ConnectorName":{"arbitrary_argument1": "aa1_value", "aa2": "aa2_value"}}'
`

This connect argument is parsed as a json, the upper level key is the class that python will attempt to import.
This class name should also be in a file that is name in all lowercase, of the same name.

Example: ConnectorName would be in file connectorname.py

The value of "ConnectorName" in our example above will all be passed to init as a dictionary. 
this means that "arbitrary_argument1" and "aa2" will both be available for the connector class
As you can see the connect argument is a json file, and as such; you may pass multiple connectors in at the same time.


Software Dependencies
====================
Pkpass has few dependencies. Fernet is a crypto library used to allow automatic symmetric encrypting.  Fernet can be installed using pip:
  pip install cryptography

Other dependencies can be found in requirements.txt  
__Note:__ All dependencies will be installed if the setup script is run.

Python 2 support
====================
We will support python2 until the end of the year, this tool was originally written in python2; and should also work with python3.

Windows Consideration
====================
There has not been much (if any) testing around the windows ecosystem. Coding has been attempted to comply with portability standards;
but compatibility is not guaranteed. If you need it, feel free to submit a PR 😀

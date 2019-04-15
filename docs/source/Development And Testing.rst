Development and Testing
=======================

Testing Scripts
---------------
Currently there exists a shell script ``./test/pki/generatepki.sh`` that will generate certificates for a developer to use for unittests
After running this script, you can run tox or the ``./unittest.sh`` file; note that ``./unittest.sh`` does not test multiple versions of
python like tox does

Plugin Behavior - Connectors
----------------------------
We currently support dropping arbitary connection plugins into ``./libpkpass/connectors`` the connectors should return
certificates, example usage here is if your organization stores certs in a custom web application, or in ldap or
the like, you can create a connector to interface with that and feed pkpass certs in this manner

Connectors will be ignored due to the gitignore, I recommend creating a separate repo for that purpose. To use
a connector pkpass needs a ``connect`` argument

.. code-block:: bash

    connect: '{"ConnectorName":{"arbitrary_argument1": "aa1_value", "aa2": "aa2_value"}}'

This connect argument is parsed as a json, the upper level key is the class that python will attempt to import.
This class name should also be in a file that is name in all lowercase, of the same name.

Example: ConnectorName would be in file connectorname.py

The value of "ConnectorName" in our example above will all be passed to init as a dictionary. 
this means that "arbitrary_argument1" and "aa2" will both be available for the connector class
As you can see the connect argument is a json file, and as such; you may pass multiple connectors in at the same time.

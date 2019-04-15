General Usage
=============

Run ./pkpass.py with the '-h' flag for a list of options as well as syntax.  Some common usage examples follow:
  - Create a new security team root password in the password store:
 
    .. code-block:: bash

       ./pkpass.py create security-team/rootpw

  - Distribute the security team root password to other team members 'foo' and 'bar':
 
    .. code-block:: bash
    
       ./pkpass.py distribute -u foo,bar security-team/rootpw

  - List the names of all passwords that have been distributed to you:
 
    .. code-block:: bash
    
       ./pkpass.py list

  - Show the infrastructure team root password:
 
    .. code-block:: bash
    
       ./pkpass.py show infra-team/rootpw

  - Show all the passwords that you know:
 
    .. code-block:: bash
    
       ./pkpass.py show -a

  - List the names of all passwords that have been distributed to user identity 'foo':
 
    .. code-block:: bash
    
       ./pkpass.py list -i foo

  - Show the users that pkpass detects certificates for in the certificate repository:
 
    .. code-block:: bash
    
       ./pkpass.py listrecipients

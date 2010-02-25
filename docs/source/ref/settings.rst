.. _ref-settings:

Settings
========

LDAP_URL
--------

Required: True

LDAP URL string. Example::

     LDAP_URL = "ldap://ldap.example.org:389/"
     LDAP_URL = "ldap://ldap1.example.org:389/ ldap://ldap2.example.org:389/"

LDAP_ADMIN_USER
---------------

Required: True

DN to bind as for admin operations. Example::
   
   LDAP_ADMIN_USER = "cn=Manager,dc=python-ldap,dc=org"

LDAP_ADMIN_PASSWORD
-------------------

Required: True

Password for admin bind user. Example::
	 
	 LDAP_ADMIN_PASSWORD = "secret"

LDAP BASE
---------

Required: True

Base string of the LDAP Tree. Example::

     LDAP_BASE = "dc=python-ldap,dc=org"

LDAP_USER_BASE
--------------

Required: True

Base for User tree. Example::
     
     LDAP_USER_BASE = "ou=VHO, %s" % LDAP_BASE

LDAP_GROUP_BASE
---------------

Required: True

Base for Group tree. Example::

     LDAP_GROUP_BASE = "ou=Group, %s" % LDAP_BASE

LDAP_ATTRS
----------

Required: True

Module of LDAP attributes definition file. See :ref:`ref-ldap_attrs_settings`
Example::

	LDAP_ATTRS = "demo.ldap_attrs"

LDAP_USE_TLS
------------

Required: False

Default: False

Whether to use TLS or not. True/False.

LAP_TLS_CA
----------

Required: If LDAP_USE_TLS = True

Location of CA certificate used for TLS. Example:
	 
	 LAP_TLS_CA = "/etc/ldap/ssl/CA.pem"




.. _ref-ldap_attrs_settings:


LDAP Attributes
===============

This file spcifies how you store users and groups in LDAP. It has several sections.

REQUIRED_USER_ATTRS
-------------------
This lists all the LDAP attributes that are required in order to create a user.
There are 3 ways to pass the values of these attributes when creating a new :class:`LDAPUser <placard.lusers.models.LDAPUser>`.

1. Pass it as keyword argument to :meth:`add_user <placard.client.LDAPClient.add_user>`

.. code-block:: python

   client.add_user(uid='test', givenName='John', sn='Smith')


2. Define a default value in DEFAULT_USER_ATTRS (see below)

3. Define a generated value in GENERATED_USER_ATTRS (see below)

If you do not set all required attributes to :meth:`add_user <placard.client.LDAPClient.add_user>` you will get a :exc:`RequiredAttributeNotGiven <placard.exceptions.RequiredAttributeNotGiven>` Exception.

Example:

.. code-block:: python

   REQUIRED_USER_ATTRS = [
     'uid', 'givenName', 'sn', 'cn', 'mail', 'objectClass', 'o',
   ]


OPTIONAL_USER_ATTRS
-------------------
Like REQUIRED_USER_ATTRS except does not return a :exc:`RequiredAttributeNotGiven <placard.exceptions.RequiredAttributeNotGiven>` Exception if not given.

Example:

.. code-block:: python

   OPTIONAL_USER_ATTRS = [
      'telephoneNumber',
   ]

DEFAULT_USER_ATTRS
------------------
A dictionary containing default values for certain attributes. 
NOTE: They have to be defined in REQUIRED_USER_ATTRS.

Example:

.. code-block:: python

   DEFAULT_USER_ATTRS = {
      'objectClass': ['inetOrgPerson', 'eduPerson', 'auEduPerson', 'top', 'schacContactLocation',],
      'eduPersonAssurance': ['1',],
      'eduPersonAffiliation': 'Affiliate',
   }

GENERATED_USER_ATTRS
--------------------
A dictionary containing generated dynamic values for certain attributes
NOTE: They have to be defined in REQUIRED_USER_ATTRS.

You can pass a function to be called when generating a certain attribute. This function must take one argument which will be a dictionary containing all currently resolved attributes.

Example:

.. code-block:: python

   def get_o_value(data):
       if data['mail'].endswith('example.org'):
       	  return 'Example'
       else:
          return 'Unknown'

   GENERATED_USER_ATTRS = {
      'cn': lambda x: '%s %s' % (str(x['givenName']), str(x['sn'])),
      'o': get_o_value,
   }

GROUPS
------
These User variables also exist for groups and work in the same way.
Use the variables:

* REQUIRED_GROUP_ATTRS
* OPTIONAL_GROUP_ATTRS
* DEFAULT_GROUP_ATTRS
* GENERATED_GROUP_ATTRS


Full Example
------------
.. code-block:: python

  from django.conf import settings


  REQUIRED_USER_ATTRS = [
    'uid', 'givenName', 'sn', 'cn', 'mail', 'objectClass', 'o', 'schacCountryOfResidence', 'eduPersonAssurance', 'eduPersonAffiliation', 'auEduPersonSharedToken',
  ] 

  OPTIONAL_USER_ATTRS = [
    'userPassword', 'raw_password', 'telephoneNumber',
  ]

  DEFAULT_USER_ATTRS = {
    'objectClass': ['inetOrgPerson', 'eduPerson', 'auEduPerson', 'top', 'schacContactLocation',],
    'eduPersonAssurance': ['1',],
    'eduPersonAffiliation': 'Affiliate',
  }

  PASSWORD_ATTRS = [
    'userPassword',
  ]


  GENERATED_USER_ATTRS = {
    'cn': lambda x: '%s %s' % (str(x['givenName']), str(x['sn'])),
  }


  REQUIRED_GROUP_ATTRS = [
    'cn', 'objectClass', 'gidNumber',
  ]

  OPTIONAL_GROUP_ATTRS = [
    'description',
  ]
  #GENERATED METHODS
  # Must take one argument which is a dictionary of the currently resolved attributes (attributes are resolved in the order above)

  def get_next_gid(data):
    from placard.client import LDAPClient
    conn = LDAPClient()
    gid = conn.get_next_gid()
    return [str(gid)]

  DEFAULT_GROUP_ATTRS = {
    'objectClass': ['posixGroup', 'top'],
  }


  GENERATED_GROUP_ATTRS = {
    'gidNumber': get_next_gid,
  }

.. _ref-client:

:class:`LDAPClient` --- LDAP Client API
=======================================

.. module:: placard.client
   :synopsis: An LDAP Client library build on top of python-ldap

.. moduleauthor:: Sam Morrison <sam@vpac.org>

.. class:: LDAPClient
   
User methods
------------
.. automethod:: LDAPClient.get_users

.. automethod:: LDAPClient.get_user

.. automethod:: LDAPClient.add_user

.. automethod:: LDAPClient.update_user

.. automethod:: LDAPClient.delete_user

.. automethod:: LDAPClient.change_password

.. automethod:: LDAPClient.check_password

.. automethod:: LDAPClient.in_ldap

.. automethod:: LDAPClient.get_group_memberships

.. automethod:: LDAPClient.search_users

   .. versionadded:: 1.0.3

.. automethod:: LDAPClient.get_new_uid

.. seealso::
   
   :class:`placard.lusers.models.LDAPUser`

Group methods
-------------
.. automethod:: LDAPClient.get_groups

.. automethod:: LDAPClient.get_group

.. automethod:: LDAPClient.add_group

.. automethod:: LDAPClient.update_group

.. automethod:: LDAPClient.delete_group

.. automethod:: LDAPClient.get_group_members

.. automethod:: LDAPClient.add_group_member

.. automethod:: LDAPClient.remove_group_member

.. automethod:: LDAPClient.get_next_gid

.. seealso::
   
   :class:`placard.lgroups.models.LDAPGroup`


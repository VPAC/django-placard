.. _ref-client:

:class:`LDAPClient` --- LDAP Client API
=======================================

.. module:: placard.client
   :synopsis: An LDAP Client library build on top of python-ldap

.. moduleauthor:: Sam Morrison <sam@vpac.org>

.. class:: LDAPClient

Takes the following optional settings. By default these options are pulled from your settings file.
 
 * url=settings.LDAP_URL
 * username=settings.LDAP_ADMIN_USER
 * password=settings.LDAP_ADMIN_PASSWORD
 * base=settings=LDAP_BASE
 * user_base=settings.LDAP_USER_BASE
 * group_base=settings.LDAP_GROUP_BASE

.. seealso::
   
   :ref:`ref-settings`
 
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


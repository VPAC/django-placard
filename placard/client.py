# Copyright 2010 VPAC
#
# This file is part of django-placard.
#
# django-placard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-placard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with django-placard  If not, see <http://www.gnu.org/licenses/>.


from django.conf import settings
from django.template.defaultfilters import dictsort

import os
import ldap
import ldap.modlist as modlist
try:
    import smbpasswd
except ImportError:
    pass


from placard.ldap_passwd import UserPassword
from placard import exceptions
from placard.lusers.models import LDAPUser
from placard.lgroups.models import LDAPGroup


if hasattr(settings, 'LDAP_USE_TLS'):
    LDAP_USE_TLS = settings.LDAP_USE_TLS
else:
    LDAP_USE_TLS = False

if LDAP_USE_TLS:
    ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, settings.LDAP_TLS_CA)


ldap_attrs = __import__(settings.LDAP_ATTRS, {}, {}, [''])



class LDAPClient(object):

    def __init__(self, 
                 url=settings.LDAP_URL, 
                 username=settings.LDAP_ADMIN_USER, 
                 password=settings.LDAP_ADMIN_PASSWORD,
                 base=settings.LDAP_BASE,
                 user_base=settings.LDAP_USER_BASE,
                 group_base=settings.LDAP_GROUP_BASE):

        l = ldap.initialize(url) 
        l.protocol_version = ldap.VERSION3

        if LDAP_USE_TLS:
            l.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
            l.start_tls_s()

        l.simple_bind_s(username, password)
        self.conn = l

        self.base = base
        self.user_base = user_base
        self.group_base = group_base
    
    def __del__(self):
        self.conn.unbind_s()


    def ldap_add(self, dn, attrs):
        ldif = modlist.addModlist(attrs)
        self.conn.add_s(dn, ldif)

    def ldap_search(self, base_dn, search_filter, retrieve_attributes=['*','+'], search_scope=ldap.SCOPE_SUBTREE):
        return self.conn.search_s(base_dn, search_scope, search_filter, retrieve_attributes)

    def ldap_modify(self, dn, old, new):
        # Convert place-holders for modify-operation using modlist-module
        for i in old.values():
            if type(i) == list:
                i.sort()
        for i in new.values():
            if type(i) == list:
                i.sort()
        if old == new:
            return

        ldif = modlist.modifyModlist(old, new)
        # Do the actual modification
        try:
            self.conn.modify_s(dn, ldif)
        except ldap.PROTOCOL_ERROR, excp:
            if not excp[0]['info'] == 'no modifications specified':
                raise ldap.PROTOCOL_ERROR
        
    def ldap_delete(self, dn):
        self.conn.delete_s(dn)
        
    
    def get_groups(self, search_filter='(&(gidNumber=*)(|(objectClass=posixGroup)(objectClass=group)))'):
        """ 
        Returns a :func:`list` of :class:`~placard.lgroups.models.LDAPGroup` objects
        """
        result_data = self.ldap_search(self.group_base, search_filter) 
        groups = []
    
        for i in result_data:
            try:
                groups.append(LDAPGroup(i))
            except:
                pass
            
        return groups


    def update_group(self, search_string, **kwargs):

        group = self.get_group(search_string)
            # Some place-holders for old and new values
        old = {}
        for k, i in kwargs.items():
            try:
                old[k] = getattr(group, k)
            except:
                pass
        new = {}
        for k, i in kwargs.items():
            if i == '':
                continue
            if k == 'objectClass' or k == 'memberUid':
                new[k] = i
            else:
                new[k] = str(i)
            
        self.ldap_modify(group.dn, old, new)

        
    def get_next_gid(self):
        result_data = self.ldap_search(self.group_base, 'cn=*') 

        groups = []
    
        for i in result_data:
            try:
                groups.append(int(i[1]['gidNumber'][0]))
            except:
                pass
        
        groups.sort()
        if not groups:
            return 10001
        return int(groups[len(groups) - 1]) + 1

    def delete_group(self, search_string):
        """
        Deletes a group based on search_string.
        """
        group = self.get_group(search_string)
        self.ldap_delete(group.dn)
            

    def add_group(self, **kwargs):
                
        attrs = {}
        for a in ldap_attrs.REQUIRED_GROUP_ATTRS:
            if a in kwargs:
                if isinstance(kwargs[a], unicode):
                    attrs[a] = str(kwargs[a])
                else:
                    attrs[a] = kwargs[a]
            elif a in ldap_attrs.DEFAULT_GROUP_ATTRS:
                attrs[a] = ldap_attrs.DEFAULT_GROUP_ATTRS[a]
            elif a in ldap_attrs.GENERATED_GROUP_ATTRS:
                attrs[a] = ldap_attrs.GENERATED_GROUP_ATTRS[a](attrs)
            else:
                raise exceptions.RequiredAttributeNotGiven('Required attribute %s not found' % a)

        for a in ldap_attrs.OPTIONAL_GROUP_ATTRS:
            if a in kwargs:
                attrs[a] = kwargs[a]

        # Do the actual synchronous add-operation to the ldapserver
        dn = 'cn=%s, %s' % (attrs['cn'], self.group_base)

        self.ldap_add(dn, attrs)

        return int(attrs['gidNumber'][0])


    def get_group(self, search_string):
        """ Returns a :class:`~placard.lgroups.models.LDAPGroup` based
        on search_string.
        
        Raises :exc:`~placard.exceptions.DoesNotExistException` if no groups exists.

        Raises :exc:`~placard.exceptions.MultipleResultsException` if more than one group
        exists for the search_string.
        """
        result_data = self.ldap_search(self.group_base, search_string)

        if len(result_data) == 1:       
            return LDAPGroup(result_data[0])
        elif len(result_data) > 1:
            raise exceptions.MultipleResultsException("""Multiple groups exist for the given search string""")
        
        raise exceptions.DoesNotExistException("""Group "%s" does not exist""" % search_string)


    def get_group_members(self, search_string):
        """ Returns a list of LDAPUser objects that are members
        of given group
        """
        members = []
        
        result_data = self.ldap_search(self.group_base, search_string) 
        gid = self.get_group(search_string).gidNumber
        if 'memberUid' in result_data[0][1]:
            for m in result_data[0][1]['memberUid']:
                try:
                    u = self.get_user("uid=%s" % m)
                    members.append(u)
                except exceptions.DoesNotExistException:
                    self.remove_group_member('gidNumber=%s' % gid, m)
        primary_members = self.ldap_search(self.user_base, 'gidNumber=%s' % gid)
        for m in primary_members:
            members.append(LDAPUser(m))
    
        return dictsort(members, "cn")


    def remove_group_member(self, search_string, uid):
        """ Removes a member from a group"""

        group = self.get_group(search_string)
        try:
            members = group.memberUid[:]
        except AttributeError:
            members = []

        try:
            members.remove(str(uid))
        except ValueError:
            # Log warning
            pass

        dn = 'cn=%s, %s' % (group.cn, self.group_base)
        
        try:
            old_members = group.memberUid[:]
        except AttributeError:
            old_members = []

        old = {'memberUid': old_members }
        new = {'memberUid': members }
        
        self.ldap_modify(dn, old, new)
        

    def add_group_member(self, search_string, uid):
        """ Adds a user to a group"""

        group = self.get_group(search_string)
        try:
            members = group.memberUid[:]
        except:
            members = []
        if uid in members:
            return
        members.append(str(uid))
        members.sort()
        dn = group.dn
        
        try:
            old = {'memberUid': group.memberUid}
        except:
            old = {'MemberUid': []}
        new = {'memberUid': members }
    
        self.ldap_modify(dn, old, new)
            

    def add_user(self, has_raw_password=False, **kwargs):
        """Creates an LDAP user"""

        attrs = {}
        for a in ldap_attrs.REQUIRED_USER_ATTRS:
            if a in kwargs:
                if isinstance(kwargs[a], unicode):
                    attrs[a] = str(kwargs[a])
                else:
                    attrs[a] = kwargs[a]
            elif a in ldap_attrs.DEFAULT_USER_ATTRS:
                attrs[a] = ldap_attrs.DEFAULT_USER_ATTRS[a]
            elif a in ldap_attrs.GENERATED_USER_ATTRS:
                attrs[a] = ldap_attrs.GENERATED_USER_ATTRS[a](attrs)
            else:
                raise exceptions.RequiredAttributeNotGiven('Required attribute %s not found' % a)

        for a in ldap_attrs.OPTIONAL_USER_ATTRS:
            if a in kwargs:
                if isinstance(kwargs[a], unicode):
                    attrs[a] = str(kwargs[a])
                else:
                    attrs[a] = kwargs[a]
            elif a in ldap_attrs.DEFAULT_USER_ATTRS:
                attrs[a] = ldap_attrs.DEFAULT_USER_ATTRS[a]
            elif a in ldap_attrs.GENERATED_USER_ATTRS:
                attrs[a] = ldap_attrs.GENERATED_USER_ATTRS[a](attrs)
                
        if has_raw_password:
            raw_password = attrs['raw_password']
        if 'raw_password' in attrs:
            del attrs['raw_password']
          
        for k, v in attrs.items():
            if v == '':
                del(attrs[k])

        rdn = getattr(settings, 'LDAP_USER_RDN', 'uid')
        dn = '%s=%s, %s' % (rdn, attrs[rdn], self.user_base)

        self.ldap_add(dn, attrs)
        
        if has_raw_password:
            self.change_password("uid=%s" % attrs['uid'], raw_password)

        return dn


    def delete_user(self, search_string):
        """
        Deletes user from LDAP and removes user from all groups
        """
        user = self.get_user(search_string)
        self.ldap_delete(user.dn)

        for g in self.get_group_memberships(user.uid):
            self.remove_group_member('gidNumber=%s' % g.gidNumber, user.uid)
        

    def change_password(self, search_string, raw_password):
        # The dn of our existing entry/object
        user = self.get_user(search_string)
        dn = user.dn
        password_attrs = getattr(ldap_attrs, 'PASSWORD_ATTRS', ['userPassword',])

        if 'userPassword' in password_attrs:
            up = UserPassword(l=self.conn, dn=dn)
            up.changePassword(newPassword=raw_password, scheme=settings.LDAP_PASSWD_SCHEME)
        if 'sambaNTPassword' in password_attrs:
            self.update_user(search_string, sambaNTPassword=smbpasswd.nthash(raw_password), sambaPwdMustChange='')
        if 'sambaLMPassword' in password_attrs:
            self.update_user(search_string, sambaLMPassword=smbpasswd.lmhash(raw_password), sambaPwdMustChange='')
        if 'unicodePwd' in password_attrs:
            unicode_password = unicode("\"" + str(raw_password) + "\"", "iso-8859-1").encode("utf-16-le")
            mod_attrs = [( ldap.MOD_REPLACE, 'unicodePwd', unicode_password),( ldap.MOD_REPLACE, 'unicodePwd', unicode_password)]
            self.conn.modify_s(dn, mod_attrs)

    def check_password(self, search_string, raw_password):
        from placard.backends import LDAPBackend
        ldap_backend = LDAPBackend()
        ldap_user = self.get_user(search_string)
        user = ldap_backend.authenticate(ldap_user.uid, raw_password)
        if user:
            return True
        else:
            return False


    def create_image(self, filename, data):
        try:
            os.remove(filename)
        except:
            pass
        from PIL import Image
        from cStringIO import StringIO
        image = Image.open(StringIO(data))
        image.save(filename, "JPEG") 

        
    def get_ldap_pic(self, uid, force=False):
        
        filename = '%s/img/users/%s.jpg' % (settings.MEDIA_ROOT, uid)
        user = self.get_user("uid=%s" % uid)

        if not 'jpegPhoto' in user.__dict__:
            return '%simg/users/none.jpg' % settings.MEDIA_URL

        if settings.DEBUG or force:
            self.create_image(filename, user.jpegPhoto)

        try:
            open(filename)
        except:
            try:
                self.create_image(filename, user.jpegPhoto)
            except:
                return ''

        return '%simg/users/%s.jpg' % (settings.MEDIA_URL, uid)
    
    def get_user(self, search_string):
        """
        returns ldap object for search_string
        raises MultipleResultsException if more than one 
        entry exists for given search string
        """
        result_data = self.ldap_search(self.user_base, search_string)
        
        no_results = len(result_data)

        if no_results > 1:
            raise exceptions.MultipleResultsException("""Search string returned more than 1 result""")

        if no_results == 1:            
            return LDAPUser(result_data[0])

        if no_results < 1:
            raise exceptions.DoesNotExistException("""User "%s" does not exist""" % search_string)


    def get_users(self, search_filter='(&(objectClass=person)(%s=*)(!(uid=nobody))(!(uid=administrator)))' % getattr(settings, 'LDAP_USER_RDN', 'uid')):
        """
        Returns a list of LDAPUser objects based on search_filter
        """
        result_data = self.ldap_search(self.user_base, search_filter)
        user_list = []
        for i in result_data:
            user_list.append(LDAPUser(i))
        return dictsort(user_list, "cn")
        
    def in_ldap(self, search_string):
        """
        Simple check to see if user in LDAP
        """
        try:
            self.get_user(search_string)
        except exceptions.DoesNotExistException:
            return False
    
        return True
        


    def update_user(self, search_string, **kwargs):
        """
        Updates a user in LDAP
        """
        ldap_user = self.get_user(search_string)
        
        # Some place-holders for old and new values
        old = {}
        for k,i in kwargs.items():
            try:
                old[k] = getattr(ldap_user, k)
            except:
                pass
        new = {}
        for k,i in kwargs.items():
            if i == '':
                continue
            if k == 'objectClass':
                new[k] = i
            else:
                new[k] = str(i)
        
        self.ldap_modify(ldap_user.dn, old, new)


    def lock_user(self, search_string):
        self.update_user(search_string, pwdAccountLockedTime='000001010000Z')

    def unlock_user(self, search_string):
        self.update_user(search_string, pwdAccountLockedTime='')

    def is_locked(self, search_string):
        ldap_user = self.get_user(search_string)
        
        if 'pwdAccountLockedTime' in ldap_user.__dict__:
            return True
        return False
        
    def get_new_uid(self):
        """Return the next available user id"""
        
        result_data = self.ldap_search(self.user_base, 'uid=*')

        id_list = []
        for i in result_data:
            try:
                id_list.append(int(i[1]['uidNumber'][0]))
            except:
                pass

        if not id_list:
            return 10001
        id_list.sort()
        id_list.reverse()
        return id_list[0] + 1


    def get_group_memberships(self, uid):
        """
        Gets all groups person is in
        """
        
        result_data = self.ldap_search(self.group_base, 'memberUid=*%s*' % uid) 
        
        groups = []
        for i in result_data:
            group = i[1]
            if 'memberUid' in i[1]:
                if uid in i[1]['memberUid']:
                    groups.append(LDAPGroup(i))

        return groups

    def search_users(self, term_list):
        
        search_fields = ldap_attrs.REQUIRED_USER_ATTRS + ldap_attrs.OPTIONAL_USER_ATTRS
        no_search_fields = ['objectClass', 'userPassword', 'raw_password']
        for s in no_search_fields:
            try:
                search_fields.remove(s)
            except ValueError:
                pass

        filter = '(&(uid=*)'

        for t in term_list:
            filter += '(|'
            for s in search_fields:
                filter += '(%s=*%s*)' % (s, t)
            filter += ')'
                
        filter += ')'
        return self.get_users(filter)


from django.core.mail import mail_admins
from django.conf import settings
from django.template.defaultfilters import dictsort

from django_common.util import unique
import time, datetime
import os
import ldap
import ldap.modlist as modlist
try:
    import smbpasswd
except:
    pass


from placard.ldap_passwd import UserPassword
from placard import exceptions
from placard.lusers.models import LDAPUser
from placard.lgroups.models import LDAPGroup


if hasattr(settings, 'LDAP_USE_TLS'):
    LDAP_USE_TLS = settings.LDAP_USE_TLS
else:
    LDAP_USE_TLS= False

if LDAP_USE_TLS:
    ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, settings.LDAP_TLS_CA)


ldap_attrs = __import__(settings.LDAP_ATTRS, {}, {}, [''])



class LDAPClient(object):

    def __init__(self, url=settings.LDAP_URL, 
                 username=settings.LDAP_ADMIN_USER, 
                 password=settings.LDAP_ADMIN_PASSWORD,
                 base=settings.LDAP_BASE,
                 user_base=settings.LDAP_USER_BASE,
                 group_base=settings.LDAP_GROUP_BASE):

        l = ldap.initialize(url) 
        l.protocol_version = ldap.VERSION3

        if LDAP_USE_TLS:
            l.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
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
        self.conn.add_s(dn,ldif)

    def ldap_search(self, baseDN, searchFilter):
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None
        return self.conn.search_s(baseDN, searchScope, searchFilter, retrieveAttributes)

    def ldap_modify(self, dn, old, new):
        # Convert place-holders for modify-operation using modlist-module
        ldif = modlist.modifyModlist(old, new)
        # Do the actual modification 
        self.conn.modify_s(dn, ldif)
        
    def ldap_delete(self, dn):
        self.conn.delete_s(dn)
        
    
    def get_groups(self, search_filter='cn=*'):
        result_data = self.ldap_search(self.group_base, search_filter) 
        groups = []
    
        for i in result_data:
            try:
                groups.append(LDAPGroup(i))
            except:
                pass
            
        return groups


    def update_group(self, gidNumber, **kwargs):

        group = self.get_group(gidNumber)
            # Some place-holders for old and new values
        old = {}
        for k,i in kwargs.items():
            try:
                old[k] = getattr(group, k)
            except:
                pass
        new = {}
        for k,i in kwargs.items():
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

    def delete_group(self, gid):
        group = self.get_group(gid)
        dn = "cn=%s, %s" % (str(group.cn), self.group_base)
        self.ldap_delete(dn)
            

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
                raise RequiredAttributeNotGiven('Required attribute %s not found' % a)

        for a in ldap_attrs.OPTIONAL_GROUP_ATTRS:
            if a in kwargs:
                attrs[a] = kwargs[a]

        # Do the actual synchronous add-operation to the ldapserver
        dn = 'cn=%s, %s' % (attrs['cn'], self.group_base)

        self.ldap_add(dn, attrs)

        return attrs['gidNumber']


    def get_group(self, gid):

        result_data = self.ldap_search(self.group_base, 'gidNumber=%s' % gid)
    
        if len(result_data) == 1:
        
            return LDAPGroup(result_data[0])

        raise exceptions.DoesNotExistException("""Group "%s" does not exist""" % gid)


    def get_group_members(self, gid):
    
        members = []
        
        result_data = self.ldap_search(self.group_base, 'gidNumber=%s' % gid) 
	if 'memberUid' in result_data[0][1]:
            for m in result_data[0][1]['memberUid']:
	        try:
                    u = self.get_user("uid=%s" % m)
                    members.append(u)
                except:
                    self.remove_group_member(gid, m)

        primary_members = self.ldap_search(self.user_base, 'gidNumber=%s' % gid)
        for m in primary_members:
            members.append(LDAPUser(m))
    
        return dictsort(members, "givenName")


    def remove_group_member(self, gidNumber, uid):
        group = self.get_group(gidNumber)
        members = group.memberUid[:]
        members.remove(str(uid))
        dn = 'cn=%s, %s' % (group.cn, self.group_base)
        
        old = {'memberUid': group.memberUid,}
        new = {'memberUid': members }
        
        self.ldap_modify(dn, old, new)
        

    def add_group_member(self, gidNumber, uid):
        group = self.get_group(gidNumber)
        try:
            members = group.memberUid[:]
        except:
            members = []
        if uid in members:
            return
        members.append(str(uid))
        members.sort()
        dn = 'cn=%s, %s' % (group.cn, self.group_base)
        
        try:
            old = {'memberUid': group.memberUid,}
        except:
            old = {'MemberUid': [],}
        new = {'memberUid': members }
    
        self.ldap_modify(dn, old, new)
            

    def get_gid(self, name):
        
        result_data = self.ldap_search(self.group_base, 'cn=%s' % name)

        if (len(result_data) != 1):
            return None
    
        return result_data[0][1]['gidNumber'][0]



    ##
    ## USER
    ##
    def add_user(self, has_raw_password=False, **kwargs):
        """Creates an LDAP user given a Person"""

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
                raise RequiredAttributeNotGiven('Required attribute %s not found' % a)

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
            del attrs['raw_password']
          
        for k,v in attrs.items():
            if v == '':
                del(attrs[k])

        dn = 'uid=%s, %s' % (attrs['uid'], self.user_base)

        self.ldap_add(dn, attrs)
        
        if has_raw_password:
            self.change_password(attrs['uid'], raw_password)

        return "Added"


    def delete_user(self, uid):
        dn = "uid=%s, %s" % (uid, self.user_base)
        self.ldap_delete(dn)    

        for g in self.get_group_memberships(uid):
            self.remove_group_member(g.gidNumber, uid)
        

    def change_password(self, username, raw_password):
        # The dn of our existing entry/object
        dn="uid=%s,%s" % (username, self.user_base)
        
        up = UserPassword(l=self.conn, dn=dn)
        up.changePassword(newPassword=raw_password, scheme=settings.LDAP_PASSWD_SCHEME)
        
        try:
            if 'sambaNTPassword' in ldap_attrs.PASSWORD_ATTRS:
                self.update_user(username, sambaNTPassword=smbpasswd.nthash(raw_password), sambaPwdMustChange='')
            if 'sambaLMPassword' in ldap_attrs.PASSWORD_ATTRS:
                self.update_user(username, sambaLMPassword=smbpasswd.lmhash(raw_password), sambaPwdMustChange='')
        except:
            pass


    def check_password(self, uid, raw_password):
        from django_common.backends.auth import LDAPBackend
        ldap_backend = LDAPBackend()
        user = ldap_backend.authenticate(uid, raw_password)
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
        returns ldap object for uid
        """
        result_data = self.ldap_search(self.user_base, search_string)
        
        no_results = len(result_data)

        if no_results > 1:
            raise exceptions.MultipleResultsException("""Search string returned more than 1 result""")

        if no_results == 1:            
            return LDAPUser(result_data[0])

        if no_results < 1:
            raise exceptions.DoesNotExistException("""User "%s" does not exist""" % search_string)


    def get_users(self, search_filter='(&(uid=*)(!(uid=nobody))(!(uid=administrator)))'):

        result_data = self.ldap_search(self.user_base, search_filter)
        user_list = []
        for i in result_data:
            user_list.append(LDAPUser(i))
        return dictsort(user_list, "givenName")
        
    def in_ldap(self, uid):
        """
        Simple check to see if user in LDAP
        """
        try:
            self.get_user('uid=%s' % uid)
        except exceptions.DoesNotExistException:
            return False
    
        return True
        


    def update_user(self, uid, **kwargs):

        try:
            ldap_user = self.get_user("uid=%s" % uid)
        
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
        except Exception, e:
            if hasattr(e, 'message'):
                if not e.message['info'] == 'no modifications specified':
                    message ="Failed to update details for '%s'\nPlease investigate\n\n%s" % (uid, e)
                    mail_admins('Placard LDAP Error',  message, fail_silently=False)                    
            elif hasattr(e, 'info'):
		if not e['info'] == 'no modifications specified':
		    message ="Failed to update details for '%s'\nPlease investigate\n\n%s" % (uid, e)
	            mail_admins('Placard LDAP Error',  message, fail_silently=False)
            elif hasattr(e, 'args'):
		if not e.args[0]['info'] == 'no modifications specified':
		    message ="Failed to update details for '%s'\nPlease investigate\n\n%s" % (uid, e)
	            mail_admins('Placard LDAP Error',  message, fail_silently=False)
  	    else:
                message ="Failed to update details for '%s'\nPlease investigate\n\n%s" % (uid, e)
                mail_admins('Placard LDAP Error',  message, fail_silently=False)


            
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
        Gets all groups prson is in
        """
        result_data = self.ldap_search(self.group_base, 'memberUid=*%s*' % uid) 
        
        groups = []
        for i in result_data:
            group = i[1]
            if 'memberUid' in i[1]:
                if uid in i[1]['memberUid']:
                    groups.append(LDAPGroup(i))

        return groups

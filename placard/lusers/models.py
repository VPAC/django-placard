from django.db import models

from placard import exceptions

class LDAPUser(object):

    def __init__(self, data):
        self.dn = data[0]
        data_dict = data[1]
        for k, v in data_dict.items():
            if len(v) == 1:
                setattr(self, k, v[0])
            else:
                setattr(self, k, v)
        
    def __unicode__(self):
        return self.cn

    def __str__(self):
        return self.dn

    def __repr__(self):
        return self.__str__()

    def photo_url(self):
        from placard import LDAPClient
        conn = LDAPClient()
        return conn.get_ldap_pic(self.uid)

    def primary_group(self):
        from placard import LDAPClient
        conn = LDAPClient()
        return conn.get_group("gidNumber=%s" % self.gidNumber)

    def secondary_groups(self):
        from placard import LDAPClient
        conn = LDAPClient()
        return conn.get_group_memberships("uid=%s" % self.uid)

    def get_manager(self):
        from placard import LDAPClient
        conn = LDAPClient()
        try:
            return conn.get_user("uid=%s" % self.manager.split(',')[0].split('=')[1])
        except exceptions.DoesNotExistException:
            return None

    @models.permalink  
    def get_absolute_url(self):
        return ('plac_user_detail', [self.uid])

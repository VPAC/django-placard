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
        from placard.client import LDAPClient
        conn = LDAPClient()
        return conn.get_ldap_pic(self.uid)

    def primary_group(self):
        from placard.client import LDAPClient
        conn = LDAPClient()
        return conn.get_group("gidNumber=%s" % self.gidNumber)

    def secondary_groups(self):
        from placard.client import LDAPClient
        conn = LDAPClient()
        return conn.get_group_memberships(self.uid)

    def get_manager(self):
        from placard.client import LDAPClient
        conn = LDAPClient()
        try:
            return conn.get_user("uid=%s" % self.manager.split(',')[0].split('=')[1])
        except exceptions.DoesNotExistException:
            return None

    @models.permalink  
    def get_absolute_url(self):
        return ('plac_user_detail', [self.uid])

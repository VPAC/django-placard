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


class LDAPGroup(object):

    def __init__(self, data):
        self.dn = data[0]
        data_dict = data[1]
        for k, v in data_dict.items():
            if len(v) == 1 and k != 'memberUid':
                setattr(self, k, v[0])
            else:
                setattr(self, k, v)
        
    def __unicode__(self):
        return u'%s' % self.__str__()

    def __str__(self):
        return self.cn

    def __repr__(self):
        return self.__str__()

    @models.permalink
    def get_absolute_url(self):
        return ('plac_grp_detail', [self.gidNumber])

    def __cmp__(self, other):
        if self.dn == other.dn:
            return 0
        return 1

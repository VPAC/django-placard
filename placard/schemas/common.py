# Copyright 2012 VPAC
#
# This file is part of django-tldap.
#
# django-tldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-tldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with django-tldap  If not, see <http://www.gnu.org/licenses/>.

import tldap

class personMixin(object):
    def __unicode__(self):
        return u"%s"%(self.displayName or self.cn)

    def check_password(self, password):
        using = self._alias
        return tldap.connections[using].check_password(self.dn, password)

    def lock_shell(self):
        if not self.loginShell.startswith("/locked"):
            self.loginShell = '/locked' + self.loginShell

    def unlock_shell(self):
        if self.loginShell.startswith("/locked"):
            self.loginShell = self.loginShell[7:]

    def set_inet_org_person_defaults(self):
        pass

    def save_inet_org_person_defaults(self):
        self.displayName = '%s %s' % (self.givenName, self.sn)


class accountMixin(object):
    def set_free_uidNumber(self):
        model = self.__class__
        uid = None
        for u in model.objects.all():
            if uid is None or u.uidNumber > uid:
                uid = u.uidNumber
        self.uidNumber = uid + 1

    def set_posix_account_defaults(self):
        self.set_free_uidNumber()
        self.loginShell = '/bin/bash'

    def set_shadow_account_defaults(self):
        self.shadowInactive = 10
        self.shadowLastChange = 13600
        self.shadowMax = 365
        self.shadowMin = 1
        self.shadowWarning = 10

    def save_posix_account_defaults(self):
        self.gecos = '%s %s' % (self.givenName, self.sn)
        if self.uid is not None:
            self.unixHomeDirectory =  '/home/%s' % self.uid

    def save_shadow_account_defaults(self):
        pass

    def prepare_for_delete(self):
        self.manager_of.clear()


class groupMixin(object):
    def __unicode__(self):
        return u"%s"%self.cn

    def set_free_gidNumber(self):
        model = self.__class__
        gid = None
        for g in model.objects.all():
            if gid is None or g.gidNumber > gid:
                gid = g.gidNumber
        self.gidNumber = gid + 1

    def set_posix_group_defaults(self):
        self.set_free_gidNumber()

    def save_posix_group_defaults(self):
        if self.description is None:
            self.description = self.cn



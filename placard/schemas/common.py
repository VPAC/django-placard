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
import datetime
import placard.models


class baseMixin(tldap.base.LDAPobject):
    mixin_list = []

    def change_password(self, password):
        for mixin in self.mixin_list:
            if hasattr(mixin, 'change_password'):
                mixin.change_password(self, password)

    def set_defaults(self):
        for mixin in self.mixin_list:
            if hasattr(mixin, 'set_defaults'):
                mixin.set_defaults(self)

    def pre_create(self, master):
        for mixin in self.mixin_list:
            if hasattr(mixin, 'pre_create'):
                mixin.pre_create(self, master)

    def post_create(self, master):
        for mixin in self.mixin_list:
            if hasattr(mixin, 'post_create'):
                mixin.post_create(self, master)

    def pre_save(self):
        for mixin in self.mixin_list:
            if hasattr(mixin, 'pre_save'):
                mixin.pre_save(self)

    def pre_delete(self):
        for mixin in self.mixin_list:
            if hasattr(mixin, 'pre_delete'):
                mixin.pre_delete(self)

    def lock(self):
        for mixin in self.mixin_list:
            if hasattr(mixin, 'lock'):
                mixin.lock(self)

    def unlock(self):
        for mixin in self.mixin_list:
            if hasattr(mixin, 'unlock'):
                mixin.unlock(self)

    def check_password(self, password):
        locked = True
        num = 0

        if self.is_locked():
            return False

        for mixin in self.mixin_list:
            if hasattr(mixin, 'check_password'):
                num = num + 1
                if not mixin.check_password(self, password):
                    locked = False

        if num == 0:
            locked = False

        return locked

    def is_locked(self):
        locked = True

        for mixin in self.mixin_list:
            if hasattr(mixin, 'is_locked'):
                if not mixin.is_locked(self):
                    locked = False

        return locked

    def __unicode__(self):
        for mixin in reversed(self.mixin_list):
            if hasattr(mixin, '__unicode__'):
                return mixin.__unicode__(self)


class personMixin(object):
    @classmethod
    def __unicode__(cls, self):
        return u"P:%s"%(self.displayName or self.cn)

    @classmethod
    def check_password(cls, self, password):
        using = self._alias
        return tldap.connections[using].check_password(self.dn, password)

    @classmethod
    def pre_create(cls, self, master):
        if self.cn is None:
            self.cn = self.uid

    @classmethod
    def pre_save(cls, self):
        self.displayName = '%s %s' % (self.givenName, self.sn)


class accountMixin(object):
    @classmethod
    def set_free_uidNumber(cls, self):
        model = self.__class__
        self.uidNumber =  placard.models.counters.get_and_increment("uidNumber", 10000,
                lambda n: len(model.objects.filter(uidNumber = n)) == 0)

    @classmethod
    def __unicode__(cls, self):
        return u"A:%s"%(self.displayName or self.cn)

    @classmethod
    def set_defaults(cls, self):
        self.loginShell = '/bin/bash'

    @classmethod
    def pre_create(cls, self, master):
        assert self.uidNumber is None
        if master is not None:
            self.uidNumber = master.uidNumber
        else:
            cls.set_free_uidNumber(self)
        if self.unixHomeDirectory is None and self.uid is not None:
            self.unixHomeDirectory =  '/home/%s' % self.uid

    @classmethod
    def pre_save(cls, self):
        self.gecos = '%s %s' % (self.givenName, self.sn)

    @classmethod
    def pre_delete(cls, self):
        self.manager_of.clear()

    @classmethod
    def lock(cls, self):
        if self.loginShell is None:
            return
        if not self.loginShell.startswith("/locked"):
            self.loginShell = '/locked' + self.loginShell

    @classmethod
    def unlock(cls, self):
        if self.loginShell is None:
            return
        if self.loginShell.startswith("/locked"):
            self.loginShell = self.loginShell[7:]


class shadowMixin(object):

    @classmethod
    def change_password(cls, self, password):
        self.shadowLastChange=datetime.datetime.now().date()


class groupMixin(object):
    # Note standard posixGroup objectClass has no displayName attribute

    @classmethod
    def set_free_gidNumber(cls, self):
        model = self.__class__
        self.gidNumber =  placard.models.counters.get_and_increment("gidNumber", 10000,
                lambda n: len(model.objects.filter(gidNumber = n)) == 0)

    @classmethod
    def __unicode__(cls, self):
        return u"G:%s"%self.cn

    @classmethod
    def pre_create(cls, self, master):
        assert self.gidNumber is None
        if master is not None:
            self.gidNumber = master.gidNumber
        else:
            cls.set_free_gidNumber(self)

    @classmethod
    def pre_save(cls, self):
        if self.description is None:
            self.description = self.cn



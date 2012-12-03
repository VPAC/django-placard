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

    def save(self, *args, **kwargs):
        for mixin in self.mixin_list:
            if hasattr(mixin, 'prepare_for_save'):
                mixin.prepare_for_save(self)
        super(baseMixin, self).save(*args, **kwargs)

    def delete(self, using=None):
        for mixin in self.mixin_list:
            if hasattr(mixin, 'prepare_for_delete'):
                mixin.prepare_for_delete(self)
        super(baseMixin, self).delete(using)

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
        num = 0

        for mixin in self.mixin_list:
            if hasattr(mixin, 'is_locked'):
                num = num + 1
                if not mixin.is_locked(self):
                    locked = False

        if num == 0:
            locked = False

        return locked

    def __unicode__(self):
        for mixin in self.mixin_list:
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
    def is_locked(cls, self):
        if self.loginShell is None:
            return False
        return self.loginShell.startswith("/locked")

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

    @classmethod
    def prepare_for_save(cls, self):
        self.displayName = '%s %s' % (self.givenName, self.sn)
        if self.cn is None:
            self.cn = uid


class accountMixin(object):
    @classmethod
    def __unicode__(cls, self):
        return u"A:%s"%(self.displayName or self.cn)

    @classmethod
    def set_defaults(cls, self):
        self.loginShell = '/bin/bash'
        self.shadowInactive = 10
        self.shadowLastChange = 13600
        self.shadowMax = 365
        self.shadowMin = 1
        self.shadowWarning = 10

    @classmethod
    def prepare_for_save(cls, self):
        self.gecos = '%s %s' % (self.givenName, self.sn)
        if self.uid is not None:
            self.unixHomeDirectory =  '/home/%s' % self.uid

    @classmethod
    def prepare_for_delete(cls, self):
        self.manager_of.clear()


class groupMixin(object):
    @classmethod
    def __unicode__(cls, self):
        return u"G:%s"%self.cn

    @classmethod
    def prepare_for_save(cls, self):
        if self.description is None:
            self.description = self.cn



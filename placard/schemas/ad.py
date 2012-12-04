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

import django.conf

class adUserMixin(object):

    @classmethod
    def set_defaults(cls, self):
        self.userAccountControl = 512

    @classmethod
    def prepare_for_save(cls, self, using):
        if self.objectSid is None:
            self.objectSid = "S-1-5-" + django.conf.settings.AD_DOMAIN_SID + "-" + str(int(self.uidNumber)*2)

    @classmethod
    def is_locked(cls, self):
        return self.userAccountControl & 0x2

    @classmethod
    def lock(cls, self):
        self.userAccountControl = self.userAccountControl | 0x2

    @classmethod
    def unlock(cls, self):
        self.userAccountControl = self.userAccountControl & 0xFFFFFFFD

    @classmethod
    def change_password(cls, self, password):
        self.account_change_password(password)
        self.userPassword = None
        self.unicodePwd = '"' + password + '"'
        self.force_replace.add('unicodePwd')


class adGroupMixin(object):

    @classmethod
    def prepare_for_save(cls, self, using):
        if self.objectSid is None:
            self.objectSid = "S-1-5-" + django.conf.settings.AD_DOMAIN_SID + "-" + str(int(self.uidNumber)*2)

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

import placard.ldap_passwd

class pwdPolicyMixin(object):
    @classmethod
    def set_defaults(cls, self):
        self.pwdAttribute = 'userPassword'

    @classmethod
    def pre_save(cls, self, using):
        if self.pwdAttribute is None:
            self.pwdAttribute = 'userPassword'

    @classmethod
    def is_locked(cls, self):
        return self.pwdAccountLockedTime is not None

    @classmethod
    def lock(cls, self):
        self.pwdAccountLockedTime='000001010000Z'

    @classmethod
    def unlock(cls, self):
        self.pwdAccountLockedTime=None

    @classmethod
    def change_password(cls, self, password):
        up = placard.ldap_passwd.UserPassword()
        self.userPassword = up.encodePassword(password, "ssha")




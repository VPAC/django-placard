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

class adUserMixin(object):

    def account_set_defaults(self):
        self.userAccountControl = 512
        self.secondary_groups.add(group.objects.get(cn="Domain Users"))
        self.objectSid = "S-1-5-" + django.conf.settings.AD_DOMAIN_SID + "-" + str(int(self.uidNumber)*2)

    def account_save_defaults(self):
        pass

    def account_is_locked(self):
        return self.userAccountControl & 0x2

    def account_lock(self):
        self.userAccountControl = self.userAccountControl | 0x2

    def account_unlock(self):
        self.userAccountControl = self.userAccountControl & 0xFFFFFFFD

    def account_change_password(self, password):
        self.account_change_password(password)
        self.userPassword = None
        self.unicodePwd = '"' + password + '"'
        self.force_replace.add('unicodePwd')


class adGroupMixin(object):

    def set_ad_group_defaults(self):
        self.objectSid = "S-1-5-" + django.conf.settings.AD_DOMAIN_SID + "-" + str(int(self.uidNumber)*2)

    def save_ad_group_defaults(self):
        pass




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
import smbpasswd

class sambaAccountMixin(object):

    def set_samba_account_defaults(self):
        self.secondary_groups.add(group.objects.get(cn="Domain Users"))
        self.sambaDomainName = django.conf.settings.SAMBA_DOMAIN_NAME
        self.sambaAcctFlags = '[ U         ]'
        self.sambaSID = "S-1-5-" + django.conf.settings.SAMBA_DOMAIN_SID + "-" + str(int(self.uidNumber)*2)
        self.sambaPwdLastSet = str(int(time.mktime(datetime.datetime.now().timetuple())))

    def save_samba_account_defaults(self):
        pass

    def samba_account_lock(self):
        self.sambaAcctFlags = '[DU         ]'

    def samba_account_unlock(self):
        self.sambaAcctFlags = '[ U         ]'

    def samba_account_change_password(self, password):
        if isinstance(password, unicode):
            password = password.encode()
        self.sambaNTPassword=smbpasswd.nthash(password)
        self.sambaLMPassword=smbpasswd.lmhash(password)
        self.sambaPwdMustChange=None
        self.sambaPwdLastSet=str(int(time.mktime(datetime.datetime.now().timetuple())))


class sambaGroupMixin(object):
    def set_samba_group_defaults(self):
        self.sambaGroupType = 2
        self.sambaSID = "S-1-5-" + django.conf.settings.SAMBA_DOMAIN_SID + "-" + str(int(self.uidNumber)*2 + 1001)

    def save_samba_group_defaults(self):
        pass


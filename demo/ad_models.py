# Copyright 2012 VPAC
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

from tldap.schemas import rfc, ad
from placard.schemas import common
from placard.schemas.ad import adUserMixin, adGroupMixin
import tldap.manager
import django.conf
import time
import datetime

import placard.ldap_passwd

##########
# person #
##########

class person(ad.person, rfc.organizationalPerson, rfc.inetOrgPerson, ad.user, common.personMixin, adUserMixin):

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'person' ])
        pk = 'cn'

    def change_password(self, password):
        self.account_change_password(password)

    def set_defaults(self):
        self.set_inet_org_person_defaults()
        self.account_set_defaults()

    def save(self, *args, **kwargs):
        self.save_inet_org_person_defaults()
        self.account_save_defaults()
        if self.cn is None:
            self.cn = self.uid
        super(person, self).save(*args, **kwargs)

    def is_locked(self):
        return self.account_is_locked()

    def lock(self):
        self.lock_shell()
        self.account_lock()

    def unlock(self):
        self.unlock_shell()
        self.account_unlock()

    managed_by = tldap.manager.ManyToOneDescriptor('manager', 'demo.ad_models.person', 'dn')
    manager_of = tldap.manager.OneToManyDescriptor('dn', 'demo.ad_models.person', 'manager')


###########
# account #
###########

class account(person, ad.posixAccount, common.accountMixin):

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'user' ])
        pk = 'cn'

    managed_by = tldap.manager.ManyToOneDescriptor('manager', 'demo.ad_models.account', 'dn')
    manager_of = tldap.manager.OneToManyDescriptor('dn', 'demo.ad_models.account', 'manager')

    def set_defaults(self):
        super(account, self).set_defaults()
        self.set_posix_account_defaults()
        self.set_shadow_account_defaults()

    def delete(self, using=None):
        self.prepare_for_delete()
        super(account, self).delete(using)

    def save(self, *args, **kwargs):
        self.save_posix_account_defaults()
        self.save_shadow_account_defaults()
        super(account, self).save(*args, **kwargs)


#########
# group #
#########

class group(rfc.posixGroup, ad.group, common.groupMixin, adGroupMixin):
    class Meta:
        base_dn_setting = "LDAP_GROUP_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'group' ])
        pk = 'cn'

    # accounts
    primary_accounts = tldap.manager.OneToManyDescriptor('gidNumber', account, 'gidNumber', "primary_group")
    secondary_accounts = tldap.manager.AdAccountLinkDescriptor(account, "secondary_groups")

    def set_defaults(self):
        self.set_posix_group_defaults()
        self.set_ad_group_defaults()

    def save(self, *args, **kwargs):
        self.save_posix_group_defaults()
        self.save_ad_group_defaults()
        super(group, self).save(*args, **kwargs)

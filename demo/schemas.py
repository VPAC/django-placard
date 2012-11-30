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
from placard.schemas.pwdpolicy import pwdPolicyMixin
from placard.schemas.ad import adUserMixin, adGroupMixin
import tldap.manager

#######
# rfc #
#######

class localRfcAccountMixin(object):
    @classmethod
    def prepare_for_save(cls, self):
        if self.cn is None:
            self.cn = '%s %s' % (self.givenName, self.sn)


class rfc_account(
        rfc.person, rfc.organizationalPerson, rfc.inetOrgPerson, rfc.pwdPolicy,
        rfc.posixAccount, rfc.shadowAccount,
        common.baseMixin):
    mixin_list = [ common.personMixin, pwdPolicyMixin, common.accountMixin, localRfcAccountMixin ]

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'posixAccount' ])
        pk = 'uid'

    managed_by = tldap.manager.ManyToOneDescriptor('manager', 'demo.schemas.rfc_account', 'dn')
    manager_of = tldap.manager.OneToManyDescriptor('dn', 'demo.schemas.rfc_account', 'manager')
    unixHomeDirectory = tldap.manager.AliasDescriptor("homeDirectory")


class rfc_group(rfc.posixGroup, common.baseMixin):
    mixin_list = [ common.groupMixin ]

    class Meta:
        base_dn_setting = "LDAP_GROUP_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'posixGroup' ])
        pk = 'cn'

    # accounts
    primary_accounts = tldap.manager.OneToManyDescriptor('gidNumber', rfc_account, 'gidNumber', "primary_group")
    secondary_accounts = tldap.manager.ManyToManyDescriptor('memberUid', rfc_account, 'uid', False, "secondary_groups")

######
# ad #
######

class localAdAccountMixin(object):
    @classmethod
    def prepare_for_save(cls, self):
        if self.cn is None:
            self.cn = self.uid


class ad_account(
        ad.person, rfc.organizationalPerson, rfc.inetOrgPerson, ad.user,
        ad.posixAccount,
        common.baseMixin):
    mixin_list = [ common.personMixin, adUserMixin, common.accountMixin, localAdAccountMixin ]

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'user' ])
        pk = 'cn'

    managed_by = tldap.manager.ManyToOneDescriptor('manager', 'demo.schemas.ad_account', 'dn')
    manager_of = tldap.manager.OneToManyDescriptor('dn', 'demo.schemas.ad_account', 'manager')


class ad_group(rfc.posixGroup, ad.group, common.baseMixin):
    mixin_list = [ common.groupMixin, adGroupMixin ]

    class Meta:
        base_dn_setting = "LDAP_GROUP_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'group' ])
        pk = 'cn'

    # accounts
    primary_accounts = tldap.manager.OneToManyDescriptor('gidNumber', ad_account, 'gidNumber', "primary_group")
    secondary_accounts = tldap.manager.AdAccountLinkDescriptor(ad_account, "secondary_groups")

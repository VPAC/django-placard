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

import django.conf

#######
# rfc #
#######

class rfc_account(
        rfc.person, rfc.organizationalPerson, rfc.inetOrgPerson, rfc.pwdPolicy,
        rfc.posixAccount, rfc.shadowAccount,
        common.baseMixin):
    mixin_list = [ common.personMixin, pwdPolicyMixin, common.accountMixin, common.shadowMixin ]

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'posixAccount' ])
        pk = 'uid'

    managed_by = tldap.manager.ManyToOneDescriptor(this_key='manager', linked_cls='placard.test.schemas.rfc_account', linked_key='dn')
    manager_of = tldap.manager.OneToManyDescriptor(this_key='dn', linked_cls='placard.test.schemas.rfc_account', linked_key='manager')
    unixHomeDirectory = tldap.manager.AliasDescriptor("homeDirectory")


class rfc_group(rfc.posixGroup, common.baseMixin):
    mixin_list = [ common.groupMixin ]

    class Meta:
        base_dn_setting = "LDAP_GROUP_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'posixGroup' ])
        pk = 'cn'

    # accounts
    primary_accounts = tldap.manager.OneToManyDescriptor(this_key='gidNumber', linked_cls=rfc_account, linked_key='gidNumber', related_name="primary_group")
    secondary_accounts = tldap.manager.ManyToManyDescriptor(this_key='memberUid', linked_cls=rfc_account, linked_key='uid', linked_is_p=False, related_name="secondary_groups")


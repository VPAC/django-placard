# Copyright 2010 VPAC
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


from django.conf import settings

GROUP_DN = settings.LDAP_GROUP_BASE
GROUP_OU = GROUP_DN.split(',')[0].split('=')[1]
USER_DN = settings.LDAP_USER_BASE
USER_OU = USER_DN.split(',')[0].split('=')[1]

settings.LDAP_GROUP_BASE.split(',')[0].split('=')[1]
test_ldif = [
    "dn: " + GROUP_DN,
    "objectClass: organizationalUnit",
    "ou: " + GROUP_OU,
    "",
    "dn: " + USER_DN,
    "objectClass: organizationalUnit",
    "ou: " + USER_OU,
    "",
    'dn: uid=testuser1, ' + settings.LDAP_USER_BASE,
    'cn: Test User',
    'objectClass: inetOrgPerson',
    'objectClass: eduPerson',
    'objectClass: auEduPerson',
    'objectClass: top',
    'objectClass: schacContactLocation',
    'userPassword:: kklk',
    'o: Example Org',
    'sn: User',
    'mail: t.user@example.com',
    'givenName: Test',
    'eduPersonAssurance: 1',
    'schacCountryOfResidence: AU',
    'uid: testuser1',
    'eduPersonAffiliation: Affiliate',
    'auEduPersonSharedToken: sdsd9894nk4',
    '',
    'dn: uid=testuser2, ' + settings.LDAP_USER_BASE,
    'cn: Test User2',
    'objectClass: inetOrgPerson',
    'objectClass: eduPerson',
    'objectClass: auEduPerson',
    'objectClass: top',
    'objectClass: schacContactLocation',
    'userPassword:: gfgf',
    'o: Example Org2',
    'sn: User2',
    'mail: t.user2@example.com',
    'givenName: Test',
    'eduPersonAssurance: 1',
    'schacCountryOfResidence: AU',
    'uid: testuser2',
    'eduPersonAffiliation: Affiliate',
    'auEduPersonSharedToken: sdsd9fsdfdsfsd894nk4',
    '',
    'dn: uid=testuser3, ' + settings.LDAP_USER_BASE,
    'cn: Test User3',
    'objectClass: inetOrgPerson',
    'objectClass: eduPerson',
    'objectClass: auEduPerson',
    'objectClass: top',
    'objectClass: schacContactLocation',
    'userPassword:: asdf',
    'o: Example Org3',
    'sn: User3',
    'mail: t.user3@example.com',
    'givenName: Test',
    'eduPersonAssurance: 1',
    'schacCountryOfResidence: AU',
    'uid: testuser3',
    'eduPersonAffiliation: Affiliate',
    'auEduPersonSharedToken: sdsd9894n34gfk4',
    '',
    'dn: cn=systems, ' + settings.LDAP_GROUP_BASE,
    'objectClass: posixGroup',
    'gidNumber: 10001',
    'cn: systems',
    'description: Systems Services',
    'memberUid: testuser1',
    '',
    'dn: cn=empty, ' + settings.LDAP_GROUP_BASE,
    'objectClass: posixGroup',
    'gidNumber: 10002',
    'cn: empty',
    'description: Empty Group',
    '',
    'dn: cn=full,' + settings.LDAP_GROUP_BASE,
    'objectClass: posixGroup',
    'gidNumber: 10003',
    'cn: full',
    'description: Full Group',
    'memberUid: testuser1',
    'memberUid: testuser2',
    'memberUid: testuser3',
    '',
    ]

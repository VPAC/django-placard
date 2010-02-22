from django.conf import settings


test_ldif = [
    "dn: " + settings.LDAP_GROUP_BASE,
    "objectClass: organizationalUnit",
    "ou: Group",
    "",
    "dn: " + settings.LDAP_USER_BASE,
    "objectClass: organizationalUnit",
    "ou: VHO",
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

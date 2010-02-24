from django.conf import settings


REQUIRED_USER_ATTRS = [
    'uid', 'givenName', 'sn', 'cn', 'mail', 'objectClass', 'o', 'schacCountryOfResidence', 'eduPersonAssurance', 'eduPersonAffiliation', 'auEduPersonSharedToken',
    ] 

OPTIONAL_USER_ATTRS = [
    'userPassword', 'raw_password', 'telephoneNumber',
]

DEFAULT_USER_ATTRS = {
    'objectClass': ['inetOrgPerson', 'eduPerson', 'auEduPerson', 'top', 'schacContactLocation',],
    'eduPersonAssurance': ['1',],
    'eduPersonAffiliation': 'Affiliate',
}

PASSWORD_ATTRS = [
    'userPassword',
    ]


GENERATED_USER_ATTRS = {
    'cn': lambda x: '%s %s' % (str(x['givenName']), str(x['sn'])),
}


REQUIRED_GROUP_ATTRS = [
    'cn', 'objectClass', 'gidNumber',
    ]

OPTIONAL_GROUP_ATTRS = [
    'description',
]
#GENERATED METHODS
# Must take one argument which is a dictionary of the currently resolved attributes (attributes are resolved in the order above)

def get_next_gid(data):
    from placard.client import LDAPClient
    conn = LDAPClient()
    gid = conn.get_next_gid()
    return [str(gid)]

DEFAULT_GROUP_ATTRS = {
    'objectClass': ['posixGroup', 'top'],
    }


GENERATED_GROUP_ATTRS = {
    'gidNumber': get_next_gid,
}

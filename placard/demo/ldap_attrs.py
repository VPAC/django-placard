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
    ]

OPTIONAL_GROUP_ATTRS = [
    
]
#GENERATED METHODS
# Must take one argument which is a dictionary of the currently resolved attributes (attributes are resolved in the order above)

DEFAULT_GROUP_ATTRS = {
    }


GENERATED_GROUP_ATTRS = {
}

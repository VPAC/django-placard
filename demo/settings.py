
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'placard',
    'placard.lusers',
    'placard.lgroups',
    'andsome',
    'andsome.layout',
)

LDAP_USE_TLS=False
LDAP_URL = 'ldap://localhost:38911'

LDAP_ADMIN_PASSWORD="password"
LDAP_BASE="dc=python-ldap,dc=org"
LDAP_ADMIN_USER="cn=Manager,dc=python-ldap,dc=org"
LDAP_USER_BASE='ou=VHO, %s' % LDAP_BASE
LDAP_GROUP_BASE='ou=Group, %s' % LDAP_BASE
LDAP_ATTRS = 'demo.ldap_attrs'


TEST_RUNNER='andsome.test_utils.xmlrunner.run_tests'
DATABASE_ENGINE = 'sqlite3'

ROOT_URLCONF = 'demo.urls'

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

DEBUG=True
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'placard.db'          # Or path to database file if using sqlite3.
DATABASE_USER = ''                    # Not used with sqlite3.
DATABASE_HOST = ''                    # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''                    # Set to empty string for default. Not used with sqlite3.

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'placard',
    'andsome',
    'andsome.layout',
)

LDAP_USE_TLS=False
LDAP_URL = 'ldap://localhost:38911'

LDAP_ADMIN_PASSWORD="password"
LDAP_BASE="dc=python-ldap,dc=org"
LDAP_ADMIN_USER="cn=Manager,dc=python-ldap,dc=org"
LDAP_USER_BASE='ou=People, %s' % LDAP_BASE
LDAP_GROUP_BASE='ou=Group, %s' % LDAP_BASE

LDAP_PASSWD_SCHEME = 'ssha'
TEST_RUNNER='andsome.test_utils.xmlrunner.run_tests'

ROOT_URLCONF = 'placard.urls'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'andsome.middleware.threadlocals.ThreadLocals',
    'django.middleware.doc.XViewMiddleware',
    'tldap.middleware.TransactionMiddleware',
)

STATIC_ROOT = '/tmp/static'
STATIC_URL = '/media/'

PLACARD_MODELS = "tldap.test.models"

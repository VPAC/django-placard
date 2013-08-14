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

from placard.settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'placard.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

LDAP = {
    'default': {
        'ENGINE': 'tldap.backend.fake_transactions',
        'URI': 'ldap://localhost:38911/',
        'USER': 'cn=Manager,dc=python-ldap,dc=org',
        'PASSWORD': 'password',
        'USE_TLS': False,
        'TLS_CA': None,
        'LDAP_ACCOUNT_BASE': 'ou=People, dc=python-ldap,dc=org',
        'LDAP_GROUP_BASE': 'ou=Group, dc=python-ldap,dc=org'
    }
}

PLACARD_MASTER = {
    'NAME': 'OpenLDAP',
    'LDAP': 'default',
    'ACCOUNT': 'placard.test.schemas.rfc_account',
    'GROUP': 'placard.test.schemas.rfc_group',
}

SECRET_KEY = '5hvhpe6gv2t5x4$3dtq(w2v#vg@)sx4p3r_@wv%l41g!stslc*'

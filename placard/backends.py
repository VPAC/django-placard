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


from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ImproperlyConfigured

import ldap
import ldap.filter


class LDAPBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        
        try:
            test = settings.LDAP_URL
            test = settings.LDAP_BASE
        except:
            raise ImproperlyConfigured("LDAP_URL and LDAP_BASE must be specified in settings.py")
        
        scope = ldap.SCOPE_SUBTREE
        filter = ldap.filter.filter_format("(&(objectclass=person) (uid=%s))", [username])
        ret = ['dn']

        try:
            l = ldap.initialize(settings.LDAP_URL)
        except ldap.LDAPError:
            return None

        try:
            result_id = l.search(settings.LDAP_BASE, scope, filter, ret)
            result_type, result_data = l.result(result_id, 0)

            # If the user does not exist in LDAP, Fail.
            if (len(result_data) != 1):
                return None

            # Attempt to bind to the user's DN
            l.simple_bind_s(result_data[0][0], password)

            # The user existed and authenticated. Get the user
            # record or create one with no privileges.
            try:
                user = User.objects.get(username__exact=username)
            except User.DoesNotExist:
                # Theoretical backdoor could be input right here. We don't
                # want that, so input an unused random password here.
                # The reason this is a backdoor is because we create a
                # User object for LDAP users so we can get permissions,
                # however we -don't- want them able to login without
                # going through LDAP with this user. So we effectively
                # disable their non-LDAP login ability by setting it to a
                # random password that is not given to them. In this way,
                # static users that don't go through ldap can still login
                # properly, and LDAP users still have a User object.
                from random import choice
                import string
                temp_pass = ""
                for i in range(16):
                    temp_pass = temp_pass + choice(string.letters)
                user = User.objects.create_user(username, '', temp_pass)
                user.is_staff = False
                user.save()
            # Success.
            return user
           
        except ldap.INVALID_CREDENTIALS:
            # Name or password were bad. Fail.
            return None
        except ldap.UNWILLING_TO_PERFORM:
            # User set inactive
            return None
            

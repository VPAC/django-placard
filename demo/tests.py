#!/usr/bin/python

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


from django.test.client import Client
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

import unittest

from tldap.test import slapd
from tldap.test.data import test_ldif

import placard.models

import ldap

class UserViewsTests(TestCase):

    def setUp(self):
        server = slapd.Slapd()
        server.set_port(38911)
        server.start()
        base = server.get_dn_suffix()

        server.ldapadd("\n".join(test_ldif)+"\n")

        self.server = server

        self.group = placard.models.group
        self.account = placard.models.account

        super_user = User.objects.create_user('super', 'sam@vpac.org', 'aq12ws')
        super_user.is_superuser = True
        super_user.save()

    def tearDown(self):
        self.server.stop()

    def test_user_list(self):
        response = self.client.get(reverse('plac_user_list'))
        self.failUnlessEqual(response.status_code, 200)

    def test_user_detail(self):
        response = self.client.get(reverse('plac_user_detail', args=['testuser1']))
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get(reverse('plac_user_detail', args=['nousers']))
        self.failUnlessEqual(response.status_code, 404)

    def test_delete_view(self):
        response = self.client.get(reverse('plac_user_delete', args=['testuser1']))
        self.failUnlessEqual(response.status_code, 302)
        self.client.login(username='super', password='aq12ws')
        response = self.client.get(reverse('plac_user_delete', args=['testuser1']))
        self.failUnlessEqual(response.status_code, 200)

    def test_user_verbose(self):
        response = self.client.get(reverse('plac_user_detail_verbose', args=['testuser2']))
        self.failUnlessEqual(response.status_code, 302)
        self.client.login(username='super', password='aq12ws')
        response = self.client.get(reverse('plac_user_detail_verbose', args=['testuser2']))
        self.failUnlessEqual(response.status_code, 200)

    def test_lock_user_view(self):
        response = self.client.get(reverse('plac_user_detail_verbose', args=['testuser2']))

    def test_lock_unlock_user_view(self):
        self.failUnlessEqual(self.account.objects.get(uid='testuser2').is_locked(), False)

        self.client.login(username='super', password='aq12ws')
        response = self.client.post(reverse('plac_lock_user', args=['testuser2']))

        self.failUnlessEqual(self.account.objects.get(uid='testuser2').is_locked(), True)

        response = self.client.post(reverse('plac_unlock_user', args=['testuser2']))

        self.failUnlessEqual(self.account.objects.get(uid='testuser2').is_locked(), False)


class PasswordTests(TestCase):

    def setUp(self):
        global server
        server = slapd.Slapd()
        server.set_port(38911)
        server.start()
        base = server.get_dn_suffix()

        server.ldapadd("\n".join(test_ldif)+"\n")

        self.server = server

        self.group = placard.models.group
        self.account = placard.models.account

        super_user = User.objects.create_user('super', 'sam@vpac.org', 'aq12ws')
        super_user.is_superuser = True
        super_user.save()

    def tearDown(self):
        self.server.stop()

    def test_api(self):
        u = self.account.objects.get(uid='testuser2')
        u.change_password('aq12ws')
        u.save()

        self.failUnlessEqual(u.check_password('aq12ws'), True)

        u = self.account.objects.get(uid='testuser3')
        u.change_password('qwerty')
        u.save()

        self.failUnlessEqual(u.check_password('qwerty'), True)

    def test_admin_view(self):
        response = self.client.get(reverse('plac_change_password', args=['testuser1']))
        self.failUnlessEqual(response.status_code, 302)
        self.client.login(username='super', password='aq12ws')
        response = self.client.get(reverse('plac_change_password', args=['testuser1']))
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.post(reverse('plac_change_password', args=['testuser1']), {'new1': 'aq12ws222', 'new2': 'aq12ws222'})
        self.failUnlessEqual(response.status_code, 302)

        u = self.account.objects.get(uid='testuser1')
        self.failUnlessEqual(u.check_password('aq12ws222'), True)

    def test_user_view(self):
        u = self.account.objects.get(uid='testuser2')
        u.change_password('aq12ws')
        u.save()

        luser = self.account.objects.get(uid='testuser2')
        user = User.objects.create_user(luser.uid, luser.mail, 'aq12ws')

        response = self.client.get(reverse('plac_user_password'))
        self.failUnlessEqual(response.status_code, 302)

        self.client.login(username='testuser2', password='aq12ws')

        response = self.client.get(reverse('plac_change_password', args=['testuser1']))
        self.failUnlessEqual(response.status_code, 403)

        response = self.client.get(reverse('plac_user_password'))
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.post(reverse('plac_user_password'), {'old': 'aq12ws', 'new1': 'aq12ws222', 'new2': 'aq12ws222'})
        self.failUnlessEqual(response.status_code, 302)

        self.failUnlessEqual(u.check_password('aq12ws222'), True)

if __name__ == '__main__':
    unittest.main()

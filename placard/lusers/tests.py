from django.test.client import Client
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

import unittest

from placard.server import slapd
from placard.client import LDAPClient
from placard.misc.test_data import test_ldif

server = None


class LDAPUsersTest(unittest.TestCase):
    def setUp(self):
        global server
        server = slapd.Slapd()
        server.set_port(38911)
        server.start()
        base = server.get_dn_suffix()
        
        server.ldapadd("\n".join(test_ldif)+"\n")

        self.client = Client()
        self.server = server
            
    def tearDown(self):
        self.server.stop()


    def test_get_users(self):
        c = LDAPClient()
        self.failUnlessEqual(len(c.get_users()), 3)
        
    def test_get_user(self):
        c = LDAPClient()      
        u = c.get_user('uid=testuser3')
        self.failUnlessEqual(u.mail, 't.user3@example.com')
                             
    def test_delete_user(self):
        c = LDAPClient()
        self.failUnlessEqual(len(c.get_users()), 3)
        c.delete_user('uid=testuser2')
        self.failUnlessEqual(len(c.get_users()), 2)
                
    def test_in_ldap(self):
        c = LDAPClient()
        self.assertTrue(c.in_ldap('uid=testuser1'))
        self.assertFalse(c.in_ldap('uid=testuser4'))
        
    def test_update_user(self):
        c = LDAPClient()
        u = c.get_user('uid=testuser1')
        self.failUnlessEqual(u.sn, 'User')  
        c.update_user('uid=%s' % u.uid, sn='Bloggs')
        u = c.get_user('uid=testuser1')
        self.failUnlessEqual(u.sn, 'Bloggs')

    def test_update_user_no_modifications(self):
        c = LDAPClient()
        u = c.get_user('uid=testuser1')
        self.failUnlessEqual(u.sn, 'User')  
        c.update_user('uid=%s' % u.uid, sn='User')
        u = c.get_user('uid=testuser1')
        self.failUnlessEqual(u.sn, 'User')

    def test_user_search(self):
        c = LDAPClient()
        users = c.search_users(['User',])
        self.failUnlessEqual(len(users), 3)

    def test_user_search_one(self):
        c = LDAPClient()
        users = c.search_users(['testuser1',])
        self.failUnlessEqual(len(users), 1)

    def test_user_search_empty(self):
        c = LDAPClient()
        users = c.search_users(['nothing',])
        self.failUnlessEqual(len(users), 0)

    def test_user_search_multi(self):
        c = LDAPClient()
        users = c.search_users(['test', 'user'])
        self.failUnlessEqual(len(users), 3)
        
        
class UserViewsTests(TestCase):

    def setUp(self):
        global server
        server = slapd.Slapd()
        server.set_port(38911)
        server.start()
        base = server.get_dn_suffix()
        
        server.ldapadd("\n".join(test_ldif)+"\n")

        self.server = server

        try:
            super_user = User.objects.create_user('super', 'sam@vpac.org', 'aq12ws')
            super_user.is_superuser = True
            super_user.save()
        except:
            pass

            
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

        

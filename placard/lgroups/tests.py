from django.test.client import Client
from django.core.urlresolvers import reverse
from django.conf import settings

import unittest

from placard import slapd
from placard import LDAPClient
from placard.misc.test_data import test_ldif

server = None


class LDAPGroupTest(unittest.TestCase):
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
        g = c.get_group('testgroup')
        self.failUnlessEqual(g.cn, 'testgroup')
                             
    def test_delete_user(self):
        c = LDAPClient()
        self.failUnlessEqual(len(c.get_groups()), 3)
        c.delete_group('testgroup2')
        self.failUnlessEqual(len(c.get_groups()), 2)
                
    def test_update(self):
        c = LDAPClient()
        g = c.get_group('testgroup3')
        self.failUnlessEqual(g.description, 'Test Group3')  
        c.update_user(g.gidNumber, cn='Systems')
        g = c.get_group('uid=testgroup3')
        self.failUnlessEqual(g.sn, 'Systems')


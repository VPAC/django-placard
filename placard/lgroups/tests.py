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


    def test_get_groups(self):
        c = LDAPClient()
        self.failUnlessEqual(len(c.get_users()), 3)
        
    def test_get_group(self):
        c = LDAPClient()      
        g = c.get_group('cn=systems')
        self.failUnlessEqual(g.cn, 'systems')
                             
    def test_delete_group(self):
        c = LDAPClient()
        self.failUnlessEqual(len(c.get_groups()), 3)
        c.delete_group('cn=full')
        self.failUnlessEqual(len(c.get_groups()), 2)
                
    def test_update(self):
        c = LDAPClient()
        g = c.get_group('cn=empty')
        self.failUnlessEqual(g.description, 'Empty')  
        c.update_user(g.gidNumber, description='No Members')
        g = c.get_group('cn=emtpy')
        self.failUnlessEqual(g.description, 'No Members')


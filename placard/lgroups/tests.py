from django.test.client import Client
from django.core.urlresolvers import reverse
from django.conf import settings

import unittest

from placard.server import slapd
from placard import LDAPClient
from placard.misc.test_data import test_ldif
from placard import exceptions

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
        self.failUnlessEqual(len(c.get_groups()), 3)
        
    def test_get_group(self):
        c = LDAPClient()      
        g = c.get_group('cn=systems')
        self.failUnlessEqual(g.cn, 'systems')
        g = c.get_group('cn=empty')
        self.failUnlessEqual(g.cn, 'empty')
        g = c.get_group('cn=full')
        self.failUnlessEqual(g.cn, 'full')
                             
    def test_delete_group(self):
        c = LDAPClient()
        self.failUnlessEqual(len(c.get_groups()), 3)
        c.delete_group('cn=full')
        self.failUnlessEqual(len(c.get_groups()), 2)
                
    def test_update_group(self):
        c = LDAPClient()
        g = c.get_group('cn=empty')
        self.failUnlessEqual(g.description, 'Empty Group')  
        c.update_group('gidNumber=%s' % g.gidNumber, description='No Members')
        g = c.get_group('cn=empty')
        self.failUnlessEqual(g.description, 'No Members')

    def test_update_group_no_modifications(self):
        c = LDAPClient()
        g = c.get_group('cn=empty')
        self.failUnlessEqual(g.description, 'Empty Group')  
        c.update_group('gidNumber=%s' % g.gidNumber, description='Empty Group')
        g = c.get_group('cn=empty')
        self.failUnlessEqual(g.description, 'Empty Group')

    def test_no_group(self):
        c = LDAPClient()
        self.failUnlessRaises(exceptions.DoesNotExistException, c.get_group, 'cn=nosuchgroup')

    def test_get_members_empty(self):
        c = LDAPClient()
        members = c.get_group_members('cn=empty')
        self.failUnlessEqual(len(members), 0)

    def test_get_members_one(self):
        c = LDAPClient()
        members = c.get_group_members('cn=systems')
        self.failUnlessEqual(len(members), 1)

    def test_get_members_many(self):
        c = LDAPClient()
        members = c.get_group_members('cn=full')
        self.failUnlessEqual(len(members), 3)
        
    def test_remove_group_member(self):
        c = LDAPClient()
        c.remove_group_member('cn=full', 'testuser2') 
        members = c.get_group_members('cn=full')
        self.failUnlessEqual(len(members), 2)

    def test_remove_group_member_one(self):
        c = LDAPClient()
        c.remove_group_member('cn=systems', 'testuser1') 
        members = c.get_group_members('cn=systems')
        self.failUnlessEqual(len(members), 0)

    def test_remove_group_member_empty(self):
        c = LDAPClient()
        c.remove_group_member('cn=empty', 'testuser1') 
        members = c.get_group_members('cn=empty')
        self.failUnlessEqual(len(members), 0)

    def test_add_member(self):
        c = LDAPClient()
        c.add_group_member('cn=systems', 'testuser2')
        members = c.get_group_members('cn=systems')
        self.failUnlessEqual(len(members), 2)

    def test_add_member_empty(self):
        c = LDAPClient()
        c.add_group_member('cn=empty', 'testuser2')
        members = c.get_group_members('cn=empty')
        self.failUnlessEqual(len(members), 1)

    def test_add_member_exists(self):
        c = LDAPClient()
        c.add_group_member('cn=full', 'testuser2')
        members = c.get_group_members('cn=full')
        self.failUnlessEqual(len(members), 3)

    def test_add_group(self):
        c = LDAPClient()
        c.add_group(cn='Admin')
        self.failUnlessEqual(len(c.get_groups()), 4)
        g = c.get_group('cn=Admin')
        self.failUnlessEqual(g.gidNumber, '10004')
        self.failUnlessEqual(g.objectClass, ['posixGroup', 'top'])
        
    def test_add_group_required_attributes(self):
        c = LDAPClient()
        self.failUnlessRaises(exceptions.RequiredAttributeNotGiven, c.add_group, description='Admin Group')

    def test_add_group_override_generated(self):
        c = LDAPClient()
        c.add_group(cn='Admin', gidNumber='10008')
        self.failUnlessEqual(len(c.get_groups()), 4)
        g = c.get_group('cn=Admin')
        self.failUnlessEqual(g.gidNumber, '10008')
        
    def test_add_group_optional(self):
        c = LDAPClient()
        c.add_group(cn='Admin', description='Admin Group')
        self.failUnlessEqual(len(c.get_groups()), 4)
        g = c.get_group('cn=Admin')
        self.failUnlessEqual(g.description, 'Admin Group')
        

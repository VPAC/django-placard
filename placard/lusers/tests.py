from django.test.client import Client
from django.core.urlresolvers import reverse
from django.conf import settings

import unittest

from placard import slapd
from placard.client import LDAPClient
from placard.lusers.models import LDAPUser

server = None


class LDAPUserTest(unittest.TestCase):
    def setUp(self):
        global server
        server = slapd.Slapd()
        server.set_port(38911)
        server.start()
        base = server.get_dn_suffix()
        
        server.ldapadd("\n".join([
                    "dn: " + settings.LDAP_GROUP_BASE,
                    "objectClass: organizationalUnit",
                    "ou: VHO",
                    "",
                    "dn: " + settings.LDAP_USER_BASE,
                    "objectClass: organizationalUnit",
                    "ou: Group",
                    "",
                    ])+"\n")

        self.client = Client()
        self.server = server

            
    def tearDown(self):
        self.server.stop()


    def test_add_user(self):
        c = LDAPClient()
        
        self.failUnlessEqual(len(c.get_users()), 0)
        

    

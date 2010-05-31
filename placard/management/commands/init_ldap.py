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

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Inititlise LDAP"
    
    def handle(self, **options):        
        verbose = int(options.get('verbosity'))
        
        from django.conf import settings
        from placard.client import LDAPClient
        import ldap

        GROUP_DN = settings.LDAP_GROUP_BASE
        GROUP_OU = GROUP_DN.split(',')[0].split('=')[1]
        USER_DN = settings.LDAP_USER_BASE
        USER_OU = USER_DN.split(',')[0].split('=')[1]

        lcon = LDAPClient()
        user_base_attrs = {
            'objectClass': ['organizationalUnit',],
            'ou': USER_OU,
            }
        
        group_base_attrs = {
            'objectClass': ['organizationalUnit',],
            'ou': GROUP_OU,
            }
        try:
            lcon.ldap_add(USER_DN, user_base_attrs)
            print "Added " + USER_DN
        except ldap.ALREADY_EXISTS:
            print USER_DN + " already exists."
        try:
            lcon.ldap_add(GROUP_DN, group_base_attrs)
            print "Added " + GROUP_DN
        except ldap.ALREADY_EXISTS:
            print GROUP_DN + " already exists."

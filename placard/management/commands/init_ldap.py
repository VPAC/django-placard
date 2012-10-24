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

import tldap.models

import ldap.dn

class Command(BaseCommand):
    help = "Inititlise LDAP"
    
    def handle(self, **options):        
        verbose = int(options.get('verbosity'))
        
        organizationalUnit = tldap.models.organizationalUnit

        from django.conf import settings

        USER_DN = settings.LDAP_USER_BASE
        GROUP_DN = settings.LDAP_GROUP_BASE

        v,c = organizationalUnit.objects.get_or_create(dn=USER_DN)
        if c:
            print "Added " + USER_DN
        else:
            print USER_DN + " already exists."

        v,c = organizationalUnit.objects.get_or_create(dn=GROUP_DN)
        if c:
            print "Added " + GROUP_DN
        else:
            print GROUP_DN + " already exists."


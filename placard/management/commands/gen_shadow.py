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

from django.core.management.base import BaseCommand

import placard.ldap_bonds as bonds

class Command(BaseCommand):
    help = "Generates a shadow file from all LDAP users"
    
    def handle(self, **options):        
        verbose = int(options.get('verbosity'))
        
        user_list = bonds.master.accounts()
        for u in user_list:
            if hasattr(u, 'userPassword'):
                p = u.userPassword
                try:
                    password = p[p.index('}')+1:]
                except:
                    password = p
                print '%s:%s' % (u.uid, password)

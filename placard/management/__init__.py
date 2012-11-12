# Copyright 2012 VPAC
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

import placard.models

from django.db.models.signals import post_syncdb
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

def create_app_permissions(sender, **kwargs):
    # create a content type for the app if it doesn't already exist
    ct, created = ContentType.objects.get_or_create(model = '', app_label = 'placard', defaults = {'name': 'placard'})

    # create a permission if it doesn't already exist
    Permission.objects.get_or_create(codename = 'add_account', content_type__pk = ct.id,
            defaults = {'name': 'Can add accounts', 'content_type': ct})
    Permission.objects.get_or_create(codename = 'change_account', content_type__pk = ct.id,
            defaults = {'name': 'Can change accounts', 'content_type': ct})
    Permission.objects.get_or_create(codename = 'change_account_password', content_type__pk = ct.id,
            defaults = {'name': 'Can change accounts\' password', 'content_type': ct})
    Permission.objects.get_or_create(codename = 'hr_change_account', content_type__pk = ct.id,
            defaults = {'name': 'HR can change accounts', 'content_type': ct})
    Permission.objects.get_or_create(codename = 'lock_account', content_type__pk = ct.id,
            defaults = {'name': 'Can lock/unlock accounts', 'content_type': ct})
    Permission.objects.get_or_create(codename = 'delete_account', content_type__pk = ct.id,
            defaults = {'name': 'Can delete accounts', 'content_type': ct})

    Permission.objects.get_or_create(codename = 'add_group', content_type__pk = ct.id,
            defaults = {'name': 'Can add groups', 'content_type': ct})
    Permission.objects.get_or_create(codename = 'email_group', content_type__pk = ct.id,
            defaults = {'name': 'Can email groups', 'content_type': ct})
    Permission.objects.get_or_create(codename = 'change_group', content_type__pk = ct.id,
            defaults = {'name': 'Can change groups', 'content_type': ct})
    Permission.objects.get_or_create(codename = 'rename_group', content_type__pk = ct.id,
            defaults = {'name': 'Can rename groups', 'content_type': ct})
    Permission.objects.get_or_create(codename = 'delete_group', content_type__pk = ct.id,
            defaults = {'name': 'Can delete groups', 'content_type': ct})

post_syncdb.connect(create_app_permissions, sender=placard.models)

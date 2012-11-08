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

import django.dispatch

args = ['user', 'data']

account_add = django.dispatch.Signal(providing_args=['user'])
account_edit = django.dispatch.Signal(providing_args=['user', 'data'])
account_password_change = django.dispatch.Signal(providing_args=['user'])
account_lock = django.dispatch.Signal(providing_args=['user'])
account_unlock = django.dispatch.Signal(providing_args=['user'])
account_delete = django.dispatch.Signal(providing_args=['user'])

group_add = django.dispatch.Signal(providing_args=['user'])
group_edit = django.dispatch.Signal(providing_args=['user', 'data'])
group_add_member = django.dispatch.Signal(providing_args=['user', 'account'])
group_remove_member = django.dispatch.Signal(providing_args=['user', 'account'])
group_delete = django.dispatch.Signal(providing_args=['user'])
group_rename = django.dispatch.Signal(providing_args=['user', 'new_pk'])
group_email = django.dispatch.Signal(providing_args=['user', 'subject', 'body'])


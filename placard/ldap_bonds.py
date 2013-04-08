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

import django.conf
import django.utils.importlib
from django.http import Http404


def _lookup(cls):
    if isinstance(cls, str):
        module_name, _, name = cls.rpartition(".")
        module = django.utils.importlib.import_module(module_name)
        try:
            cls = getattr(module, name)
        except AttributeError:
            raise AttributeError("%s reference cannot be found" % cls)
    return(cls)


class bond(object):
    def __init__(self, settings, slave_id):
        self._slave_id = slave_id
        self._name = settings['NAME']
        self._using = settings['LDAP']
        self._account = _lookup(settings['ACCOUNT'])
        self._group = _lookup(settings['GROUP'])

    def accounts(self):
        return self._account.objects.using(self._using)

    def groups(self):
        return self._group.objects.using(self._using)

    def get_account_or_404(self, *args, **kwargs):
        """
        Uses get() to return a account, or raises a Http404 exception if the
        account does not exist.

        Note: Like with get(), an MultipleObjectsReturned will be raised if
        more than one account is found.
        """
        queryset = self._account.objects.using(self._using)
        try:
            return queryset.get(*args, **kwargs)
        except queryset.model.DoesNotExist:
            raise Http404('No %s matches the given query.' % queryset.model._meta.object_name)

    def get_group_or_404(self, *args, **kwargs):
        """
        Uses get() to return a group, or raises a Http404 exception if the
        group does not exist.

        Note: Like with get(), an MultipleObjectsReturned will be raised if
        more than one group is found.
        """
        queryset = self._group.objects.using(self._using)
        try:
            return queryset.get(*args, **kwargs)
        except queryset.model.DoesNotExist:
            raise Http404('No %s matches the given query.' % queryset.model._meta.object_name)

    def create_account(self):
        return self._account(using=self._using)

    def create_group(self):
        return self._group(using=self._using)

    def __unicode__(self):
        return unicode(self._name)

    @property
    def slave_id(self):
        return self._slave_id

    @property
    def using(self):
        return self._using

    @property
    def AccountDoesNotExist(self):
        return self._account.DoesNotExist

    @property
    def GroupDoesNotExist(self):
        return self._group.DoesNotExist

master = bond(django.conf.settings.PLACARD_MASTER, slave_id=None)
slaves = {}
for slave_id, s in getattr(django.conf.settings, 'PLACARD_SLAVES', {}).iteritems():
        slaves[slave_id] = bond(s, slave_id=slave_id)

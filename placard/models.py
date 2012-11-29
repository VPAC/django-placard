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

def _lookup(cls):
    if isinstance(cls, str):
        module_name, _, name = cls.rpartition(".")
        module = django.utils.importlib.import_module(module_name)
        try:
            cls = getattr(module, name)
        except AttributeError:
            raise AttributeError("%s reference cannot be found" % cls)
    return(cls)

account = _lookup(django.conf.settings.PLACARD_SCHEMA_ACCOUNT)
group = _lookup(django.conf.settings.PLACARD_SCHEMA_GROUP)

def get_slave_accounts():
    models = getattr(django.conf.settings, 'PLACARD_SLAVES', {})
    modules = {}
    for slave_id, s in models.iteritems():
        module = _lookup(s['ACCOUNT'])
        modules[slave_id] = module
    return modules


def get_slave_account_by_id(slave_id):
    models = getattr(django.conf.settings, 'PLACARD_SLAVES', {})
    s = models[slave_id]
    return _lookup(s['ACCOUNT'])


def get_slave_groups():
    models = getattr(django.conf.settings, 'PLACARD_SLAVES', {})
    modules = {}
    for slave_id, s in models.iteritems():
        module = _lookup(s['GROUP'])
        modules[slave_id] = module
    return modules


def get_slave_group_by_id(slave_id):
    models = getattr(django.conf.settings, 'PLACARD_SLAVES', {})
    s = models[slave_id]
    return _lookup(s['GROUP'])


def get_slave_ids():
    models = getattr(django.conf.settings, 'PLACARD_SLAVES', {})
    ids = []
    for slave_id, s in models.iteritems():
        ids.append(slave_id)
    return ids


def get_slave_name_by_id(slave_id):
    models = getattr(django.conf.settings, 'PLACARD_SLAVES', {})
    s = models[slave_id]
    return s['NAME']

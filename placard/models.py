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

module = django.utils.importlib.import_module(django.conf.settings.PLACARD_MODELS)

account = module.account
group = module.group

def get_slaves():
    models = getattr(django.conf.settings, 'PLACARD_SLAVES', {})
    slaves = []
    for i, j in models.iteritems():
        module = django.utils.importlib.import_module(j)
        slaves.append((i, module))
    return slaves

def get_slave_by_name(name):
    models = getattr(django.conf.settings, 'PLACARD_SLAVES', {})
    j = models[name]
    return django.utils.importlib.import_module(j)

def get_slave_names():
    models = getattr(django.conf.settings, 'PLACARD_SLAVES', {})
    names = []
    for i, j in models.iteritems():
        names.append(i)
    return names

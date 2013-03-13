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

from django.db import models


class counters(models.Model):
    name = models.CharField(max_length=20, db_index=True)
    count = models.IntegerField()

    @classmethod
    def get_and_increment(cls, name, default, test):
        entry, c = cls.objects.select_for_update().get_or_create(name=name, defaults={'count': default})

        while not test(entry.count):
            entry.count = entry.count + 1

        n = entry.count

        entry.count = entry.count + 1
        entry.save()

        return n

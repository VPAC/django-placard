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

from django.utils.safestring import mark_safe
from django.http import QueryDict
import datetime
from operator import itemgetter


def get_query_string(qs):
    qd = QueryDict("",mutable=True)
    for k, v in qs.items():
        qd[k] = v
    return "?" + qd.urlencode()


class Filter(object):

    def __init__(self, request, name, filters, header=None):

        if header is None:
            self.header = name
        else:
            self.header = header

        self.name = name
        self.filters = filters
        self.selected = None
        if request.GET.has_key(name):
            self.selected = request.GET[name]


    def output(self, qs):

        if qs.has_key(self.name):
            del(qs[self.name])

        output = ''
        output += '<h3>By %s</h3>\n' % self.header.replace('_', ' ')
        output += '<ul>\n'
        filters = sorted(self.filters.iteritems(), key=itemgetter(1))

        if self.selected is not None:
            output += '<li><a href="%s">All</a></li>\n' % get_query_string(qs)
        else:
            output += '<li class="selected"><a href="%s">All</a></li>\n' % get_query_string(qs)
        for k, v in filters:
            if str(self.selected) == str(k):
                style = 'class="selected" '
            else:
                style = ""
            qs[self.name] = k
            output += '<li %s><a href="%s">%s</a></li>\n' % (style, get_query_string(qs), v)

        output += '</ul>'

        return output


class FilterBar(object):

    def __init__(self, request, filter_list):

        self.request = request
        self.filter_list = filter_list
        qs = request.GET.copy()

        self.qs = qs

    def output(self):

        output = ''

        for f in self.filter_list:
            output += f.output(self.qs.copy())

        return output

    def __str__(self):
        return mark_safe(self.output())


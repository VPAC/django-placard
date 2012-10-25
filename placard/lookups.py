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

from django.utils.html import escape
from django.core.urlresolvers import reverse

import placard.models

import ajax_select
import tldap

class LookupChannel(ajax_select.LookupChannel):

    def get_objects(self, ids):
        """ Get the currently selected objects when editing an existing model """
        # return in the same order as passed in here
        # this will be however the related objects Manager returns them
        # which is not guaranteed to be the same order they were in when you last edited
        # see OrdredManyToMany.md
        results = []
        query = self.model.objects.none()
        for i in ids:
            query = query | self.model.objects.filter(pk=i)

        results.extend(query)
        return results


class AccountLookup(LookupChannel):

    model = placard.models.account

    def get_query(self, q, request):
        return self.model.objects.filter(tldap.Q(cn__contains=q) | tldap.Q(uid__contains=q))

    def get_result(self, obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.cn

    def format_match(self, obj):
        """ (HTML) formatted item for display in the dropdown """
        result=[]
        if obj.jpegPhoto is not None:
            result.append(u"<img width='50' src='%s' alt='' />" % (reverse("plac_user_photo", args=[obj.uid])))
        result.append(u"%s<div><i>%s</i></div>" % (escape(obj.cn), escape(obj.mail)))
        return u"".join(result)

    def format_item_display(self, obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return u"%s<div><i>%s</i></div>" % (escape(obj.cn), escape(obj.mail))

class GroupLookup(LookupChannel):

    model = placard.models.group

    def get_query(self, q, request):
        return self.model.objects.filter(tldap.Q(cn__contains=q) | tldap.Q(description__contains=q))

    def get_result(self, obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.cn

    def format_match(self, obj):
        """ (HTML) formatted item for display in the dropdown """
        return self.format_item_display(obj)

    def format_item_display(self, obj):
        """ (HTML) formatted item for display in the dropdown """
        result = []
        result.append(u"%s" % escape(obj.cn))
        if obj.description is not None:
            result.append(u"<div><i>%s</i></div>" % escape(obj.description))
        return u"".join(result)

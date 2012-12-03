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

import placard.views
import placard.logging.models

from django.shortcuts import get_object_or_404

class LogView(placard.views.ListView):
    model = placard.logging.models.LogEntry
    template_name = "placard_log_list.html"
    context_object_name = "log_list"

    def get_context_data(self, **kwargs):
        context = super(LogView, self).get_context_data(**kwargs)

        context['Type'] = None
        context['object'] = None
        if self.kwargs.has_key('account'):
            context['type'] = u"Account"
            context['object'] = self.object
        elif self.kwargs.has_key('group'):
            context['type'] = u"Account"
            context['object'] = self.object
        elif self.kwargs.has_key('user'):
            context['type'] = u"User"
            context['object'] = self.object

        return context

    def get_queryset(self):
        qs = self.model.objects.all()

        if self.kwargs.has_key('account'):
            self.object = get_object_or_404(placard.models.account, uid=self.kwargs['account'])
            qs = qs.filter(object_dn = self.object.dn)
        elif self.kwargs.has_key('group'):
            self.object = get_object_or_404(placard.models.group, cn=self.kwargs['group'])
            qs = qs.filter(object_dn = self.object.dn)
        elif self.kwargs.has_key('user'):
            self.object = self.kwargs['user']
            qs = qs.filter(user__username__exact=self.object)

        return qs

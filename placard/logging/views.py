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

class LogView(placard.views.ListView):
    model = placard.logging.models.LogEntry
    template_name = "placard_log_list.html"
    context_object_name = "log_list"

    def check_permissions(self, request, kwargs):
        if kwargs.has_key('username'):
            self.permissions = [ 'auth.change_user' ]
        elif kwargs.has_key('group'):
            self.permissions = [ 'auth.change_group' ]
        else:
            self.permissions = [ 'auth.change_user' ]
        return super(LogView, self).check_permissions(request, kwargs)

    def get_queryset(self):
        qs = self.model.objects.all()

        if self.kwargs.has_key('username'):
            username = self.kwargs['username']
            qs = qs.filter(object_pk=username, object_type="account")
        elif self.kwargs.has_key('group'):
            group = self.kwargs['group']
            qs = qs.filter(object_pk=group, object_type="group")
        elif self.kwargs.has_key('user'):
            user = self.kwargs['user']
            qs = qs.filter(user__username=user)

        return qs

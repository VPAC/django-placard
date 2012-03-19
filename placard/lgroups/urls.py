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


from django.conf.urls.defaults import *


urlpatterns = patterns('placard.lgroups.views',
    url(r'^$', 'group_list', name='plac_grp_list'),
    url(r'^add/$', 'add_edit_group', name='plac_grp_add'),
    url(r'^(?P<group_id>\d+)/$', 'group_detail', name='plac_grp_detail'),
    url(r'^(?P<group_id>\d+)/delete/$', 'delete_group', name='plac_grp_delete'),
    url(r'^(?P<group_id>\d+)/rename/$', 'rename_group', name='plac_grp_rename'),
    url(r'^(?P<group_id>\d+)/verbose/$', 'group_detail_verbose', name='plac_group_detail_verbose'),
    url(r'^(?P<group_id>\d+)/send_mail/$', 'send_members_email', name='plac_group_email'),
    url(r'^(?P<group_id>\d+)/remove/(?P<user_id>[-.\w]+)/$', 'remove_member', name='plac_grp_rm_member'),
)

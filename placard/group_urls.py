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

from django.conf.urls.defaults import *

import placard.views as views
import placard.reports as reports

urlpatterns = patterns('',
    url(r'^$', views.GroupList.as_view(), name='plac_group_list'),
    url(r'^add/$', views.GroupEdit.as_view(), name='plac_group_add'),
    url(r'^(?P<group>[-.\w ]+)/$', views.GroupDetail.as_view(), name='plac_group_detail'),
    url(r'^(?P<group>[-.\w ]+)/add/$', views.GroupAddMember.as_view(), name='plac_group_add_member'),
    url(r'^(?P<group>[-.\w ]+)/delete/$', views.GroupDelete.as_view(), name='plac_group_delete'),
    url(r'^(?P<group>[-.\w ]+)/edit/$', views.GroupEdit.as_view(), name='plac_group_edit'),
    url(r'^(?P<group>[-.\w ]+)/remove/(?P<account>[-.\w\$]+)/$', views.GroupRemoveMember.as_view(), name='plac_group_rm_member'),
    url(r'^(?P<group>[-.\w ]+)/rename/$', views.GroupRename.as_view(), name='plac_group_rename'),
    url(r'^(?P<group>[-.\w ]+)/send_mail/$', views.GroupEmail.as_view(), name='plac_group_email'),
    url(r'^(?P<group>[-.\w ]+)/verbose/$', views.GroupVerbose.as_view(), name='plac_group_detail_verbose'),
    url(r'^(?P<group>[-.\w ]+)/source/(?P<slave>[-.\w\$]+)/$', views.GroupDetail.as_view(), name='plac_group_detail'),
    url(r'^(?P<group>[-.\w ]+)/source/(?P<slave>[-.\w\$]+)/verbose/$', views.GroupVerbose.as_view(), name='plac_group_detail_verbose'),
)

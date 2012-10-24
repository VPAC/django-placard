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
from django.contrib import admin

import placard.views as views
import placard.reports as reports

import ajax_select.urls

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='plac_index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^lookup/', include(ajax_select.urls)),

    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),

    url(r'^search/$', views.search, name='plac_search'),
    url(r'^change_password/$', views.UserChangePassword.as_view(), name='plac_user_password'),

    url(r'^staff/$', views.StaffList.as_view(), name='vpac_staff'),

    url(r'^users/$', views.AccountList.as_view(), name='plac_user_list'),
    url(r'^users/pdf/$', reports.user_list_pdf, name='plac_user_list_pdf'),
    url(r'^users/add/$', views.AccountAdd.as_view(), name='plac_user_add'),
    url(r'^users/(?P<username>[-.\w]+)/$', views.AccountDetail.as_view(), name='plac_user_detail'),
    url(r'^users/(?P<username>[-.\w]+)/add/$', views.AccountAddGroup.as_view(), name='plac_user_add_group'),
    url(r'^users/(?P<username>[-.\w]+)/change_password/$', views.AccountChangePassword.as_view(), name='plac_change_password'),
    url(r'^users/(?P<username>[-.\w]+)/delete/$', views.AccountDelete.as_view(), name='plac_user_delete'),
    url(r'^users/(?P<username>[-.\w]+)/edit/$', views.AccountEdit.as_view(), name='plac_user_edit'),
    url(r'^users/(?P<username>[-.\w]+)/groups/$', views.AccountGroups.as_view(), name='plac_users_groups'),
    url(r'^users/(?P<username>[-.\w]+)/lock/$', views.AccountLock.as_view(), name='plac_lock_user'),
    url(r'^users/(?P<username>[-.\w]+)/photo/$', views.account_photo, name='plac_user_photo'),
    url(r'^users/(?P<username>[-.\w]+)/remove/(?P<group_id>\d+)/$', views.AccountRemoveGroup.as_view(), name='plac_user_rm_group'),
    url(r'^users/(?P<username>[-.\w]+)/unlock/$', views.AccountUnlock.as_view(), name='plac_unlock_user'),
    url(r'^users/(?P<username>[-.\w]+)/verbose/$', views.AccountVerbose.as_view(), name='plac_user_detail_verbose'),

    url(r'^groups/$', views.GroupList.as_view(), name='plac_grp_list'),
    url(r'^groups/add/$', views.GroupEdit.as_view(), name='plac_grp_add'),
    url(r'^groups/(?P<group_id>\d+)/$', views.GroupDetail.as_view(), name='plac_grp_detail'),
    url(r'^groups/(?P<group_id>\d+)/add/$', views.GroupAddMember.as_view(), name='plac_grp_add_member'),
    url(r'^groups/(?P<group_id>\d+)/delete/$', views.GroupDelete.as_view(), name='plac_group_delete'),
    url(r'^groups/(?P<group_id>\d+)/edit/$', views.GroupEdit.as_view(), name='plac_grp_edit'),
    url(r'^groups/(?P<group_id>\d+)/remove/(?P<username>[-.\w]+)/$', views.GroupRemoveMember.as_view(), name='plac_grp_rm_member'),
    url(r'^groups/(?P<group_id>\d+)/rename/$', views.GroupRename.as_view(), name='plac_grp_rename'),
    url(r'^groups/(?P<group_id>\d+)/send_mail/$', views.GroupEmail.as_view(), name='plac_group_email'),
    url(r'^groups/(?P<group_id>\d+)/verbose/$', views.GroupVerbose.as_view(), name='plac_grp_detail_verbose'),
)

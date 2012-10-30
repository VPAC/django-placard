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
    url(r'^$', views.AccountList.as_view(), name='plac_user_list'),
    url(r'^pdf/$', reports.user_list_pdf, name='plac_user_list_pdf'),
    url(r'^add/$', views.AccountAdd.as_view(), name='plac_user_add'),
    url(r'^(?P<username>[-.\w]+)/$', views.AccountDetail.as_view(), name='plac_user_detail'),
    url(r'^(?P<username>[-.\w]+)/add/$', views.AccountAddGroup.as_view(), name='plac_user_add_group'),
    url(r'^(?P<username>[-.\w]+)/change_password/$', views.AccountChangePassword.as_view(), name='plac_change_password'),
    url(r'^(?P<username>[-.\w]+)/delete/$', views.AccountDelete.as_view(), name='plac_user_delete'),
    url(r'^(?P<username>[-.\w]+)/edit/$', views.AccountEdit.as_view(), name='plac_user_edit'),
    url(r'^(?P<username>[-.\w]+)/groups/$', views.AccountGroups.as_view(), name='plac_users_groups'),
    url(r'^(?P<username>[-.\w]+)/lock/$', views.AccountLock.as_view(), name='plac_lock_user'),
    url(r'^(?P<username>[-.\w]+)/photo/$', views.account_photo, name='plac_user_photo'),
    url(r'^(?P<username>[-.\w]+)/remove/(?P<group>[-.\w ]+)/$', views.AccountRemoveGroup.as_view(), name='plac_user_rm_group'),
    url(r'^(?P<username>[-.\w]+)/unlock/$', views.AccountUnlock.as_view(), name='plac_unlock_user'),
    url(r'^(?P<username>[-.\w]+)/verbose/$', views.AccountVerbose.as_view(), name='plac_user_detail_verbose'),
)

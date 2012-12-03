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
    url(r'^$', views.AccountList.as_view(), name='plac_account_list'),
    url(r'^pdf/$', reports.PdfAccountList.as_view(), name='plac_account_list_pdf'),
    url(r'^add/$', views.AccountAdd.as_view(), name='plac_account_add'),
    url(r'^(?P<account>[-.\w\$]+)/$', views.AccountDetail.as_view(), name='plac_account_detail'),
    url(r'^(?P<account>[-.\w\$]+)/add/$', views.AccountAddGroup.as_view(), name='plac_account_add_group'),
    url(r'^(?P<account>[-.\w\$]+)/change_password/$', views.AccountChangePassword.as_view(), name='plac_change_password'),
    url(r'^(?P<account>[-.\w\$]+)/delete/$', views.AccountDelete.as_view(), name='plac_account_delete'),
    url(r'^(?P<account>[-.\w\$]+)/edit/$', views.AccountEdit.as_view(), name='plac_account_edit'),
    url(r'^(?P<account>[-.\w\$]+)/lock/$', views.AccountLock.as_view(), name='plac_lock_user'),
    url(r'^(?P<account>[-.\w\$]+)/photo/$', views.account_photo, name='plac_account_photo'),
    url(r'^(?P<account>[-.\w\$]+)/remove/(?P<group>[-.\w ]+)/$', views.AccountRemoveGroup.as_view(), name='plac_account_rm_group'),
    url(r'^(?P<account>[-.\w\$]+)/unlock/$', views.AccountUnlock.as_view(), name='plac_unlock_user'),
    url(r'^(?P<account>[-.\w\$]+)/verbose/$', views.AccountVerbose.as_view(), name='plac_account_detail_verbose'),
    url(r'^(?P<account>[-.\w\$]+)/source/(?P<slave>[-.\w\$]+)/$', views.AccountDetail.as_view(), name='plac_account_detail'),
    url(r'^(?P<account>[-.\w\$]+)/source/(?P<slave>[-.\w\$]+)/verbose/$', views.AccountVerbose.as_view(), name='plac_account_detail_verbose'),
)

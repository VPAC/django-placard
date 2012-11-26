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

import placard.user_urls
import placard.group_urls

import ajax_select.urls

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='plac_index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^lookup/', include(ajax_select.urls)),

    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),

    url(r'^search/$', views.search, name='plac_search'),
    url(r'^password/$', views.UserChangePassword.as_view(), name='plac_user_password'),

    url(r'^users/', include(placard.user_urls)),
    url(r'^groups/', include(placard.group_urls)),
)

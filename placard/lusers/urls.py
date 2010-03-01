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


urlpatterns = patterns('placard.lusers',

                       
    url(r'^$', 'views.user_list', name='plac_user_list'),
    url(r'^add/$', 'views.add_edit_user', name='plac_user_add'),
#    url(r'^pdf/$', 'reports.user_list_pdf', name='plac_user_list_pdf'),
                        
    url(r'^(?P<username>[-.\w]+)/$', 'views.user_detail', name='plac_user_detail'),
    url(r'^(?P<username>[-.\w]+)/verbose/$', 'views.user_detail_verbose', name='plac_user_detail_verbose', ),
    url(r'^(?P<username>[-.\w]+)/edit/$', 'views.add_edit_user', name='plac_user_edit'),
    url(r'^(?P<username>[-.\w]+)/delete/$', 'views.delete_user', name='plac_user_delete'),
    url(r'^(?P<username>[-.\w]+)/change_password/$', 'views.change_password', name='plac_change_password'),
#    url(r'^(?P<group_id>\d+)/remove/(?P<user_id>\d+)/$', 'remove_member', name='plac_grp_rm_member'),
)
                                    

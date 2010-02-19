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
                                    

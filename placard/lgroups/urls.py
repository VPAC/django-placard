from django.conf.urls.defaults import *


urlpatterns = patterns('placard.lgroups.views',

                       
    url(r'^$', 'group_list', name='plac_grp_list'),
    url(r'^add/$', 'add_edit_group', name='plac_grp_add'),
                        
    url(r'^(?P<group_id>\d+)/$', 'group_detail', name='plac_grp_detail'),
    url(r'^(?P<group_id>\d+)/delete/$', 'delete_group', name='plac_grp_delete'),
    url(r'^(?P<group_id>\d+)/verbose/$', 'group_detail_verbose', name='plac_group_detail_verbose', ),
    url(r'^(?P<group_id>\d+)/remove/(?P<user_id>[.\w]+)/$', 'remove_member', name='plac_grp_rm_member'),
)
                        

from django.conf.urls.defaults import *
from placard.forms import SetPasswordForm, PasswordResetForm


urlpatterns = patterns('',
     (r'^users/', include('placard.lusers.urls')),    
     (r'^groups/', include('placard.lgroups.urls')),    

)

set_password_dict = {
    'set_password_form': SetPasswordForm,
}
password_reset_dict = {
    'password_reset_form': PasswordResetForm,
}

urlpatterns += patterns('django.contrib.auth.views',
     url(r'^accounts/login/$', 'login', name='login'),
     url(r'^accounts/logout/$', 'logout', name='logout'),
     url(r'^accounts/password_reset/$', 'password_reset', password_reset_dict, name='password_reset'),
     url(r'^accounts/password_reset/done/$', 'password_reset_done', name='password_reset_done'),
     url(r'^accounts/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm', set_password_dict, name='password_reset_confirm'),
     url(r'^accounts/reset/done/$', 'password_reset_complete', name='password_reset_complete'),
)


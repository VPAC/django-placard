from django import forms
from django_common.middleware.threadlocals import get_current_user
from django.conf import settings

import os, datetime, time
from placard.client import LDAPClient

class BasicLDAPUserForm(forms.Form):
    givenName = forms.CharField(label='First Name')
    sn = forms.CharField(label='Last Name')
    


class LDAPAdminPasswordForm(forms.Form):
    new1 = forms.CharField(widget=forms.PasswordInput(), label=u'New Password')
    new2 = forms.CharField(widget=forms.PasswordInput(), label=u'New Password (again)')

    def clean(self):
        data = self.cleaned_data

        if data.get('new1') and data.get('new2'):

            if data['new1'] != data['new2']:
                raise forms.ValidationError(u'You must type the same password each time')

            return data

    def save(self, username):        
        data = self.cleaned_data
        conn = LDAPClient()
        conn.change_password(username, data['new1'])
        ldap_user = conn.get_user('uid=%s' % username)
        if hasattr(ldap_user, 'sambaPwdLastSet'):
            conn.update_user(username, sambaPwdLastSet=str(int(time.mktime(datetime.datetime.now().timetuple()))))

        
class LDAPPasswordForm(LDAPAdminPasswordForm):
    old = forms.CharField(widget=forms.PasswordInput(), label='Old password')

    def clean_old(self):
        user = get_current_user()
	conn = LDAPClient()
        if not conn.check_password(user.username, self.cleaned_data['old']):
            raise forms.ValidationError(u'Your old password was incorrect')
        return self.cleaned_data['old']


class AddMemberForm(forms.Form):
    add_user = forms.ChoiceField(choices=[('','-------------')]+[(x.uid, x.cn) for x in LDAPClient().get_users()])

    def save(self, gidNumber):
        conn = LDAPClient()
        conn.add_group_member(gidNumber, self.cleaned_data['add_user'])

""" placard.lusers.forms """

from django import forms
from django_common.middleware.threadlocals import get_current_user

import datetime, time

from placard import LDAPClient
from placard.utils import is_password_strong


class BasicLDAPUserForm(forms.Form):
    """ Basic form used for sub classing """
    givenName = forms.CharField(label='First Name')
    sn = forms.CharField(label='Last Name')
    


class LDAPAdminPasswordForm(forms.Form):
    """ Password change form for admin. No old password needed. """
    new1 = forms.CharField(widget=forms.PasswordInput(), label=u'New Password')
    new2 = forms.CharField(widget=forms.PasswordInput(), label=u'New Password (again)')

    def clean(self):
        data = self.cleaned_data

        if data.get('new1') and data.get('new2'):

            if data['new1'] != data['new2']:
                raise forms.ValidationError(u'You must type the same password each time')

            if not is_password_strong(data['new1']):
                raise forms.ValidationError(u'Your password was found to be insecure, a good password has a combination of letters (upercase, lowercase), numbers and is at least 8 characters long.')
            
            return data

    def save(self, username):        
        data = self.cleaned_data
        conn = LDAPClient()
        conn.change_password('uid=%s' % username, data['new1'])
        ldap_user = conn.get_user('uid=%s' % username)
        if hasattr(ldap_user, 'sambaPwdLastSet'):
            conn.update_user('uid=%s' % username, sambaPwdLastSet=str(int(time.mktime(datetime.datetime.now().timetuple()))))

        
class LDAPPasswordForm(LDAPAdminPasswordForm):
    """ Password change form for user. Muse specify old password. """
    old = forms.CharField(widget=forms.PasswordInput(), label='Old password')

    def clean_old(self):
        user = get_current_user()
        conn = LDAPClient()
        if not conn.check_password('uid=%s' % user.username, self.cleaned_data['old']):
            raise forms.ValidationError(u'Your old password was incorrect')
        return self.cleaned_data['old']


class AddMemberForm(forms.Form):
    """ Add a user to a group form """
    add_user = forms.ChoiceField(choices=[('','-------------')]+[(x.uid, x.cn) for x in LDAPClient().get_users()])

    def save(self, gidNumber):
        conn = LDAPClient()
        conn.add_group_member('gidNumber=%s' % gidNumber, self.cleaned_data['add_user'])


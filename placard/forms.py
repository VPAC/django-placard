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


from django import forms
from django.contrib.auth.forms import PasswordResetForm as BasePasswordResetForm
from django.contrib.auth.forms import SetPasswordForm as BaseSetPasswordForm
from django.contrib.auth.models import User

from placard.client import LDAPClient
from andsome.util import is_password_strong


def sync_users():
    conn = LDAPClient()

    for luser in conn.get_users():
        try:
            user = User.objects.get(username__exact=luser.uid)
        except User.DoesNotExist:
            user = User.objects.create_user(luser.uid, luser.mail)

        user.email = luser.mail
        user.first_name = luser.givenName
        user.last_name = luser.sn
        user.save()



class PasswordResetForm(BasePasswordResetForm):
    
    def clean_email(self):
        """
        Validates that a user exists with the given e-mail address.
        """
        sync_users()
        conn = LDAPClient()
        email = self.cleaned_data["email"]
        luser_list = conn.get_users('mail=%s' % email)
        self.users_cache = User.objects.filter(username__in=[x.uid for x in luser_list])
        if len(self.users_cache) == 0:
            raise forms.ValidationError("That e-mail address doesn't have an associated user account. Are you sure you've registered?")



class SetPasswordForm(BaseSetPasswordForm):
    
    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')

        if not is_password_strong(password1):
            raise forms.ValidationError(u'Your password was found to be insecure, a good password has a combination of letters (upercase, lowercase), numbers and is at least 8 characters long.')
                        
        return password1


    def save(self, commit=True):
        conn = LDAPClient()
        conn.change_password("uid=%s" % self.user.username, self.cleaned_data['new_password1'])
        return self.user

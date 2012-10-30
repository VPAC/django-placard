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

import django.forms as forms
import django.template

from PIL import Image
from cStringIO import StringIO
import os

import tldap
import placard.models
import placard.fields as fields

import ajax_select.fields

from andsome.util import is_password_strong

AFFILIATIONS = (
    ('staff', 'Staff'),
    ('student', 'Student'),
    ('affiliate', 'Affiliate'),
)


class AutoCompleteSelectField(ajax_select.fields.AutoCompleteSelectField):
    pass

class LDAPForm(forms.Form):
    def __init__(self, *args, **kwargs):
        if self.object is None and self.model is None:
            raise RuntimeError("If creating an object we need a model to be specified")

        super(LDAPForm, self).__init__(*args, **kwargs)

        if self.object is None:
            return

        field_names = self.object._meta.get_all_field_names()
        for name in list(self.fields):
            if name not in field_names:
                continue
            value = getattr(self.object, name)
            self.initial[name] = value

    def save(self, commit=True):
        if self.object is None:
            self.object = self.model()
            self.object.set_defaults()

        field_names = self.object._meta.get_all_field_names()
        for name in list(self.fields):
            if name not in field_names:
                continue
            value = self.cleaned_data[name]
            setattr(self.object, name, value)

        if commit:
            self.object.save()

        return self.object


class LDAPUserForm(LDAPForm):
    model = placard.models.account

    givenName = fields.CharField(label='First Name')
    sn = fields.CharField(label='Last Name')
    telephoneNumber = fields.CharField(label="Phone", required=False)
    description = fields.CharField(widget=forms.Textarea(attrs={'class':'vLargeTextField', 'rows':10, 'cols':40 }), required=False)
    facsimileTelephoneNumber = fields.CharField(label="Fax", required=False)
    mobile = fields.CharField(label="Mobile", required=False)
    jpegPhoto = forms.ImageField(label='Photo', required=False)
    title = fields.CharField(widget=forms.TextInput(attrs={ 'size':60 }))
    managed_by = AutoCompleteSelectField('account', required=False)
    eduPersonAffiliation = forms.ChoiceField(label="Affiliation", choices=AFFILIATIONS, initial='staff')
    sshPublicKey = fields.CharField(label="SSH pub-key", required=False)
    l = fields.CharField(label='Location', required=False)
    loginShell = fields.CharField(label='Login Shell', required=False)

    def __init__(self, *args, **kwargs):
        self.object = kwargs.pop('account', None)
        super(LDAPUserForm, self).__init__(*args, **kwargs)

        if getattr(self, 'primary_groups', None) is not None:
            all_groups = placard.models.group.objects.none()
            for cn in self.primary_groups:
                all_groups = all_groups | placard.models.group.objects.filter(cn=cn)
            self.fields['primary_group'] = forms.ChoiceField(choices=[('','None')]+[(x.gidNumber, x.cn) for x in all_groups], label="Primary Group")
        else:
            self.fields['primary_group'] = AutoCompleteSelectField('group', required=True)

        if self.object is not None:
            managed_by = self.object.managed_by.get_obj()
            if managed_by is not None:
                self.initial['managed_by'] = managed_by.pk
            primary_group = self.object.primary_group.get_obj()
            if primary_group is not None:
                if getattr(self, 'primary_groups', None) is not None:
                    self.initial['primary_group'] = primary_group.gidNumber
                else:
                    self.initial['primary_group'] = primary_group.pk

    def clean_jpegPhoto(self):
        data = self.cleaned_data
        if data['jpegPhoto'] is None:
            jpegPhoto = None
        elif isinstance(data['jpegPhoto'], str):
            jpegPhoto = data['jpegPhoto']
        elif data['jpegPhoto'] is not None:
            uf = data['jpegPhoto']
            image = Image.open(StringIO(uf.read()))
            image.thumbnail((300, 400), Image.ANTIALIAS)
            image.save('/tmp/ldap_photo', 'JPEG')

            f = open('/tmp/ldap_photo')
            jpegPhoto = f.read()
            f.close()
            os.remove('/tmp/ldap_photo')

        return jpegPhoto

    def clean_primary_group(self):
        pg = self.cleaned_data['primary_group']
        if getattr(self, 'primary_groups', None) is not None:
            try:
                pg = placard.models.group.objects.get(gidNumber=pg)
            except placard.models.group.DoesNotExist:
                raise forms.ValidationError("The group does not exist")
        return pg

    def save(self, commit=True):
        self.object = super(LDAPUserForm, self).save(commit=False)
        self.object.managed_by = self.cleaned_data['managed_by']
        self.object.primary_group = self.cleaned_data['primary_group']
        if commit:
            self.object.save()
        return self.object

class LDAPHrUserForm(LDAPForm):
    model = placard.models.account

    givenName = fields.CharField(label='First Name')
    sn = fields.CharField(label='Last Name')
    telephoneNumber = fields.CharField(label="Phone", required=False)
    description = fields.CharField(widget=forms.Textarea(attrs={'class':'vLargeTextField', 'rows':10, 'cols':40 }), required=False)
    facsimileTelephoneNumber = fields.CharField(label="Fax", required=False)
    mobile = fields.CharField(label="Mobile", required=False)
    jpegPhoto = forms.ImageField(label='Photo', required=False)
    title = fields.CharField(widget=forms.TextInput(attrs={ 'size':60 }))
    managed_by = AutoCompleteSelectField('account', required=False)
    l = fields.CharField(label='Location', required=False)

    def __init__(self, *args, **kwargs):
        self.object = kwargs.pop('account', None)
        super(LDAPHrUserForm, self).__init__(*args, **kwargs)

        all_users =  placard.models.account.objects.all()
        if self.object.manager is not None:
            self.initial['managed_by'] = self.object.managed_by.pk

    def clean_jpegPhoto(self):
        data = self.cleaned_data
        if data['jpegPhoto'] is None:
            jpegPhoto = None
        elif isinstance(data['jpegPhoto'], str):
            jpegPhoto = data['jpegPhoto']
        elif data['jpegPhoto'] is not None:
            uf = data['jpegPhoto']
            image = Image.open(StringIO(uf.read()))
            image.thumbnail((300, 400), Image.ANTIALIAS)
            image.save('/tmp/ldap_photo', 'JPEG')

            f = open('/tmp/ldap_photo')
            jpegPhoto = f.read()
            f.close()
            os.remove('/tmp/ldap_photo')

        return jpegPhoto

    def save(self, commit=True):
        self.object = super(LDAPHrUserForm, self).save(commit=False)
        self.object.managed_by = self.cleaned_data['managed_by']
        if commit:
            self.object.save()
        return self.object


class LDAPAddUserForm(LDAPUserForm):
    uid = forms.RegexField(label="Username", max_length=15, regex=r'^\w+$')
    raw_password = fields.CharField(widget=forms.PasswordInput(), label=u'New Password')
    raw_password2 = fields.CharField(widget=forms.PasswordInput(), label=u'New Password (again)')

    def clean_jpegPhoto(self):
        data = self.cleaned_data
        if data['jpegPhoto'] is None:
            jpegPhoto = None
        elif isinstance(data['jpegPhoto'], str):
            jpegPhoto = data['jpegPhoto']
        elif data['jpegPhoto'] is not None:
            uf = data['jpegPhoto']
            image = Image.open(StringIO(uf.read()))
            image.thumbnail((300, 400), Image.ANTIALIAS)
            image.save('/tmp/ldap_photo', 'JPEG')

            f = open('/tmp/ldap_photo')
            jpegPhoto = f.read()
            f.close()
            os.remove('/tmp/ldap_photo')

        return jpegPhoto

    def clean_uid(self):
        username = self.cleaned_data['uid']
        try:
            placard.models.account.objects.get(uid=username)
        except placard.models.account.DoesNotExist:
            return username
        raise forms.ValidationError(u'Username exists')

    def clean(self):
        data = self.cleaned_data

        username = data['uid']
        if not username.islower():
            username = username.lower()

        if 'raw_password' not in data or 'raw_password2' not in data:
            return data

        if data['raw_password'] != data['raw_password2']:
            raise forms.ValidationError(u'You must type the same password each time')

        return data


class LDAPAdminPasswordForm(forms.Form):
    """ Password change form for admin. No old password needed. """

    new1 = fields.CharField(widget=forms.PasswordInput(), label=u'New Password')
    new2 = fields.CharField(widget=forms.PasswordInput(), label=u'New Password (again)')

    def __init__(self, *args, **kwargs):
        self.object = kwargs.pop('account')
        super(LDAPAdminPasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = self.cleaned_data

        if data.get('new1') and data.get('new2'):

            if data['new1'] != data['new2']:
                raise forms.ValidationError(u'You must type the same password each time')

            if not is_password_strong(data['new1']):
                raise forms.ValidationError(u'Your password was found to be insecure, a good password has a combination of letters (upercase, lowercase), numbers and is at least 8 characters long.')

            return data

    def save(self):
        data = self.cleaned_data
        self.object.change_password(data['new1'], django.conf.settings.LDAP_PASSWD_SCHEME)
        self.object.save()
        return self.object


class LDAPPasswordForm(LDAPAdminPasswordForm):
    """ Password change form for user. Muse specify old password. """
    old = fields.CharField(widget=forms.PasswordInput(), label='Old password')

    def clean_old(self):
        data = self.cleaned_data
        if not self.object.check_password(data['old']):
            raise forms.ValidationError(u'Your old password was incorrect')
        return self.cleaned_data['old']


class LDAPGroupForm(LDAPForm):
    """ Add/modify a group form"""

    model = placard.models.group
    displayName = fields.CharField('Display name', required=False)
    description = fields.CharField('Description', required=False)
    cn = fields.CharField(label='CN')

    def __init__(self, *args, **kwargs):
        self.object = kwargs.pop('group', None)
        super(LDAPGroupForm, self).__init__(*args, **kwargs)
        if self.object is not None:
            self.fields['cn'].widget.attrs['readonly'] = True

    def clean_cn(self):
        cn = self.cleaned_data['cn']
        if self.object is None:
            groups = placard.models.group.objects.filter(cn=cn)
            if len(groups) > 0:
                raise forms.ValidationError("This group already exists!")
        else:
            if self.object.cn != cn:
                raise forms.ValidationError(u'Cannot change value of uid')
        return cn


class AddMemberForm(LDAPForm):
    """ Add a user to a group form """
    account = AutoCompleteSelectField('account', required=True, label="Add user")

    def __init__(self, *args, **kwargs):
        self.object = kwargs.pop('group')
        super(AddMemberForm, self).__init__(*args, **kwargs)
#        all_users =  placard.models.account.objects.all()
#        self.fields['add_user'] = forms.ChoiceField(choices=[('','-------------')]+[(x.uid, x.cn) for x in all_users])

    def save(self, commit=True):
        user = self.cleaned_data['account']
        self.object.secondary_accounts.add(user, commit)
        return self.object


class RemoveMemberForm(LDAPForm):
    """ Add a user to a group form """

    def __init__(self, *args, **kwargs):
        self.object = kwargs.pop('group')
        self.account = kwargs.pop('account')
        super(RemoveMemberForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        self.object.secondary_accounts.remove(self.account, commit)
        return self.object


class LockAccountForm(LDAPForm):
    """ Delete a group """

    def __init__(self, *args, **kwargs):
        self.object = kwargs.pop('account')
        super(LockAccountForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        self.object.lock()
        if commit:
            self.object.save()
        return self.object

class UnlockAccountForm(LDAPForm):
    """ Delete a group """

    def __init__(self, *args, **kwargs):
        self.object = kwargs.pop('account')
        super(UnlockAccountForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        self.object.unlock()
        if commit:
            self.object.save()
        return self.object


class DeleteAccountForm(LDAPForm):
    """ Delete a group """

    def __init__(self, *args, **kwargs):
        self.object = kwargs.pop('account')
        super(DeleteAccountForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        self.object.primary_group = placard.models.group.objects.get(cn="visitor")
        self.object.secondary_groups.clear()
        self.object.lock()
        if commit:
            self.object.save()
        return self.object


class AddGroupForm(LDAPForm):
    """ Add a group to a account form """
    group = AutoCompleteSelectField('group', required=True, label="Add group")

    def __init__(self, *args, **kwargs):
        self.object = kwargs.pop('account')
        super(AddGroupForm, self).__init__(*args, **kwargs)
#        all_groups = placard.models.group.objects.all()
#        self.fields['add_group'] = forms.ChoiceField(choices=[('','None')]+[(x.gidNumber, x.cn) for x in all_groups])

    def save(self, commit=True):
        group = self.cleaned_data['group']
        self.object.secondary_groups.add(group)
        return self.object


class RemoveGroupForm(LDAPForm):
    """ Add a user to a group form """

    def __init__(self, *args, **kwargs):
        self.object = kwargs.pop('account')
        self.group = kwargs.pop('group')
        super(RemoveGroupForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        self.object.secondary_groups.remove(self.group)
        return self.object


class RenameGroupForm(LDAPForm):
    """ Rename a group """
    cn = fields.CharField(label="Name")

    def __init__(self, *args, **kwargs):
        self.object = kwargs.pop('group')
        super(RenameGroupForm, self).__init__(*args, **kwargs)


    def save(self, commit=True):
        cn = self.cleaned_data['cn']
        self.object.rename(cn=cn)
        return self.object


class EmailForm(forms.Form):
    subject = fields.CharField(widget=forms.TextInput(attrs={ 'size':60 }))
    body = fields.CharField(widget=forms.Textarea(attrs={'class':'vLargeTextField', 'rows':10, 'cols':40 }))

    def __init__(self, *args, **kwargs):
        self.object = kwargs.pop('group')
        super(EmailForm, self).__init__(*args, **kwargs)

    def get_data(self):
        return self.cleaned_data['subject'], self.cleaned_data['body']

    def save(self, commit=True):
        group = self.object

        def list_all_people():
            for i in group.primary_accounts.all():
                yield i
            for i in group.secondary_accounts.all():
                yield i

        subject_t = self.cleaned_data['subject']
        body_t = self.cleaned_data['subject']
        members = list_all_people()
        emails = []
        for member in members:
            if member.mail is not None:
                ctx = django.template.Context({
                        'first_name': member.givenName,
                        'last_name': member.sn,
                        })
                subject = django.template.Template(subject_t).render(ctx)
                body = django.template.Template(body_t).render(ctx)
                emails.append((subject, body, django.conf.settings.DEFAULT_FROM_EMAIL, [member.mail]))
#        if emails:
#            send_mass_mail(emails)

        return self.object


class DeleteGroupForm(LDAPForm):
    """ Delete a group """

    def __init__(self, *args, **kwargs):
        self.object = kwargs.pop('group')
        super(DeleteGroupForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        self.object.delete()
        return None


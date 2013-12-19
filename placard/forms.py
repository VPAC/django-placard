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

import placard.fields as fields
import placard.signals
import placard.util

import ajax_select.fields


class AutoCompleteSelectField(ajax_select.fields.AutoCompleteSelectField):
    pass


class LDAPForm(forms.Form):
    signal_add = None
    signal_edit = None

    def __init__(self, user, master_obj, slave_objs, created=False, *args, **kwargs):
        self.user = user
        self.bond, self.object = master_obj
        self.master_obj = master_obj
        self.slave_objs = slave_objs
        self.created = created

        super(LDAPForm, self).__init__(*args, **kwargs)

        field_names = self.object._meta.get_all_field_names()
        for name in list(self.fields):
            if name not in field_names:
                continue
            value = getattr(self.object, name)
            self.initial[name] = value

    def commit(self, commit):
        # if commit is False, nothing for us to do
        if not commit:
            return

        # newly created object? send trigger
        if self.created:
            for _, obj in self.slave_objs:
                obj.setup_from_master(master=self.object)

        # do the save
        self.object.save()
        for _, obj in self.slave_objs:
            obj.save()

        # signal must be activated after saving, as saving completes the DN
        if self.created:
            assert self.object.dn is not None
            self.signal_add.send(self.object, user=self.user)

    def save(self, commit=True):
        if not self.created:
            self.signal_edit.send(self.object, user=self.user, data=self.cleaned_data)

        for _, obj in [self.master_obj] + self.slave_objs:
            field_names = obj._meta.get_all_field_names()
            for name in list(self.fields):
                if name not in field_names:
                    continue
                value = self.cleaned_data[name]
                setattr(obj, name, value)

        self.commit(commit)
        return self.object


class AccountForm(LDAPForm):
    pass


class GroupForm(LDAPForm):
    pass


class LDAPAccountForm(AccountForm):
    givenName = fields.CharField(label='First Name')
    sn = fields.CharField(label='Last Name')
    telephoneNumber = fields.CharField(label="Phone", required=False)
    description = fields.CharField(widget=forms.Textarea(attrs={'class': 'vLargeTextField', 'rows': 10, 'cols': 40}), required=False)
    facsimileTelephoneNumber = fields.CharField(label="Fax", required=False)
    mobile = fields.CharField(label="Mobile", required=False)
    mail = fields.CharField(label="Email", required=True)
    jpegPhoto = forms.ImageField(label='Photo', required=False)
    title = fields.CharField(widget=forms.TextInput(attrs={'size': 60}))
    managed_by = AutoCompleteSelectField('account', required=False)
    l = fields.CharField(label='Location', required=False)
    roomNumber = fields.CharField(label='Room Number', required=False)
    loginShell = fields.CharField(label='Login Shell', required=False)

    signal_add = placard.signals.account_add
    signal_edit = placard.signals.account_edit

    def __init__(self, *args, **kwargs):
        super(LDAPAccountForm, self).__init__(*args, **kwargs)

        if getattr(self, 'primary_groups', None) is not None:
            all_groups = self.bond.groups().none()
            for cn in self.primary_groups:
                all_groups = all_groups | self.bond.groups().filter(cn=cn)
            self.fields['primary_group'] = forms.ChoiceField(choices=[('', 'None')]+[(x.cn, x.cn) for x in all_groups], label="Primary Group")
        else:
            self.fields['primary_group'] = AutoCompleteSelectField('group', required=True)

        if self.object is not None:
            managed_by = self.object.managed_by.get_obj()
            if managed_by is not None:
                self.initial['managed_by'] = managed_by.pk
            primary_group = self.object.primary_group.get_obj()
            if primary_group is not None:
                self.initial['primary_group'] = primary_group.cn

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
                pg = self.bond.groups().get(cn=pg)
            except self.bond.GroupDoesNotExist:
                raise forms.ValidationError("The group does not exist")
        return pg

    def save(self, commit=True):
        self.object = super(LDAPAccountForm, self).save(commit=False)

        self.object.managed_by = self.cleaned_data['managed_by']
        self.object.primary_group = self.cleaned_data['primary_group']

        for bond, obj in self.slave_objs:
            if self.cleaned_data['managed_by'] is not None:
                obj.managed_by = bond.accounts().get(pk=self.cleaned_data['managed_by'].pk)
            else:
                obj.managed_by = None

            if self.cleaned_data['primary_group'] is not None:
                obj.primary_group = bond.groups().get(pk=self.cleaned_data['primary_group'].pk)
            else:
                obj.primary_group = None

        self.commit(commit)
        return self.object


class LDAPHrAccountForm(AccountForm):
    givenName = fields.CharField(label='First Name')
    sn = fields.CharField(label='Last Name')
    telephoneNumber = fields.CharField(label="Phone", required=False)
    description = fields.CharField(widget=forms.Textarea(attrs={'class': 'vLargeTextField', 'rows': 10, 'cols': 40}), required=False)
    facsimileTelephoneNumber = fields.CharField(label="Fax", required=False)
    mobile = fields.CharField(label="Mobile", required=False)
    jpegPhoto = forms.ImageField(label='Photo', required=False)
    title = fields.CharField(widget=forms.TextInput(attrs={'size': 60}))
    managed_by = AutoCompleteSelectField('account', required=False)
    l = fields.CharField(label='Location', required=False)

    signal_add = placard.signals.account_add
    signal_edit = placard.signals.account_edit

    def __init__(self, *args, **kwargs):
        super(LDAPHrAccountForm, self).__init__(*args, **kwargs)

        if self.object is not None:
            managed_by = self.object.managed_by.get_obj()
            if managed_by is not None:
                self.initial['managed_by'] = managed_by.pk

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
        self.object = super(LDAPHrAccountForm, self).save(commit=False)

        self.object.managed_by = self.cleaned_data['managed_by']

        for bond, obj in self.slave_objs:
            if self.cleaned_data['managed_by'] is not None:
                obj.managed_by = bond.accounts().get(pk=self.cleaned_data['managed_by'].pk)
            else:
                obj.managed_by = None

        self.commit(commit)
        return self.object


class LDAPAddAccountForm(LDAPAccountForm):
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
        username = username.lower()
        try:
            self.bond.accounts().get(uid=username)
        except self.bond.AccountDoesNotExist:
            return username
        raise forms.ValidationError(u'Username exists')

    def clean(self):
        data = super(LDAPAddAccountForm, self).clean()

        if 'raw_password' not in data or 'raw_password2' not in data:
            return data

        if data['raw_password'] != data['raw_password2']:
            raise forms.ValidationError(u'You must type the same password each time')

        return data

    def save(self, commit=True):
        self.object = super(LDAPAddAccountForm, self).save(commit=False)
        data = self.cleaned_data

        self.object.change_password(data['raw_password'])
        for _, obj in self.slave_objs:
            obj.change_password(data['raw_password'])

        self.commit(commit)
        return self.object

class LDAPAdminPasswordForm(AccountForm):
    """ Password change form for admin. No old password needed. """

    new1 = fields.CharField(widget=forms.PasswordInput(), label=u'New Password')
    new2 = fields.CharField(widget=forms.PasswordInput(), label=u'New Password (again)')

    def clean(self):
        data = self.cleaned_data

        if data.get('new1') and data.get('new2'):

            if data['new1'] != data['new2']:
                raise forms.ValidationError(u'You must type the same password each time')

            if not placard.util.is_password_strong(data['new1']):
                raise forms.ValidationError(u'Your password was found to be insecure, a good password has a combination of letters (upercase, lowercase), numbers and is at least 8 characters long.')

            return data

    def save(self, commit=True):
        placard.signals.account_password_change.send(self.object, user=self.user)
        data = self.cleaned_data

        self.object.change_password(data['new1'])
        for _, obj in self.slave_objs:
            obj.change_password(data['new1'])

        self.commit(commit)
        return self.object


class LDAPPasswordForm(LDAPAdminPasswordForm):
    """ Password change form for user. Muse specify old password. """
    old = fields.CharField(widget=forms.PasswordInput(), label='Old password')

    def clean_old(self):
        data = self.cleaned_data
        if not self.object.check_password(data['old']):
            raise forms.ValidationError(u'Your old password was incorrect')
        return self.cleaned_data['old']


class LDAPGroupForm(GroupForm):
    """ Add/modify a group form"""
    displayName = fields.CharField(label='Display name', required=False, widget=forms.TextInput(attrs={'size': 60}))
    description = fields.CharField(label='Description', required=False, widget=forms.TextInput(attrs={'size': 60}))
    cn = fields.CharField(label='CN')

    signal_add = placard.signals.group_add
    signal_edit = placard.signals.group_edit

    def __init__(self, *args, **kwargs):
        super(LDAPGroupForm, self).__init__(*args, **kwargs)
        if not self.created:
            self.fields['cn'].widget.attrs['readonly'] = True

    def clean_cn(self):
        cn = self.cleaned_data['cn']
        if self.created:
            groups = self.bond.groups().filter(cn=cn)
            if len(groups) > 0:
                raise forms.ValidationError("This group already exists!")
        else:
            if self.object.cn != cn:
                raise forms.ValidationError(u'Cannot change value of cn')
        return cn


class AddMemberForm(GroupForm):
    """ Add a user to a group form """
    account = AutoCompleteSelectField('account', required=True, label="Add user")

    def save(self, commit=True):
        user = self.cleaned_data['account']
        placard.signals.group_add_member.send(self.object, user=self.user, account=user)

        self.object.secondary_accounts.add(self.cleaned_data['account'], commit=False)
        if commit:
            self.object.save()

        for bond, obj in self.slave_objs:
            obj.secondary_accounts.add(bond.accounts().get(pk=self.cleaned_data['account'].pk), commit=False)

        self.commit(commit)
        return self.object


class RemoveMemberForm(GroupForm):
    """ Add a user to a group form """

    def __init__(self, account, *args, **kwargs):
        self.account = account
        super(RemoveMemberForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        placard.signals.group_remove_member.send(self.object, user=self.user, account=self.account)
        self.object.secondary_accounts.remove(self.account, commit=False)
        if commit:
            self.object.save()

        for bond, obj in self.slave_objs:
            obj.secondary_accounts.remove(bond.accounts().get(pk=self.account.pk), commit=False)

        self.commit(commit)
        return self.object


class LockAccountForm(AccountForm):
    """ Lock account """

    def save(self, commit=True):
        placard.signals.account_lock.send(self.object, user=self.user)

        self.object.lock()
        for _, obj in self.slave_objs:
            obj.lock()

        self.commit(commit)
        return self.object


class UnlockAccountForm(AccountForm):
    """ Unlock account """

    def save(self, commit=True):
        placard.signals.account_unlock.send(self.object, user=self.user)

        self.object.unlock()
        for _, obj in self.slave_objs:
            obj.unlock()

        self.commit(commit)
        return self.object


class DeleteAccountForm(AccountForm):
    """ Delete account """

    def save(self, commit=True):
        placard.signals.account_delete.send(self.object, user=self.user)

        self.object.delete()

        for obj in self.slave_objs:
            obj.delete()
        return None


class AddGroupForm(AccountForm):
    """ Add a group to a account form """
    group = AutoCompleteSelectField('group', required=True, label="Add group")

    def save(self, commit=True):
        group = self.cleaned_data['group']
        placard.signals.group_add_member.send(group, user=self.user, account=self.object)

        self.object.secondary_groups.add(self.cleaned_data['group'], commit=False)

        for bond, obj in self.slave_objs:
            obj.secondary_groups.add(bond.groups().get(pk=self.cleaned_data['group'].pk), commit=False)

        self.commit(commit)
        return self.object


class RemoveGroupForm(AccountForm):
    """ Add a user to a group form """

    def __init__(self, group, *args, **kwargs):
        self.group = group
        super(RemoveGroupForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        placard.signals.group_remove_member.send(self.group, user=self.user, account=self.object)

        self.object.secondary_groups.remove(self.group, commit=False)

        for bond, obj in self.slave_objs:
            obj.secondary_groups.remove(bond.groups().get(pk=self.group.pk), commit=False)

        self.commit(commit)
        return self.object


class RenameGroupForm(GroupForm):
    """ Rename a group """
    cn = fields.CharField(label="Name")

    def save(self, commit=True):
        cn = self.cleaned_data['cn']
        old_dn = self.object.dn
        old_pk = self.object.cn

        self.object.rename(cn=cn)
        for _, obj in self.slave_objs:
            obj.rename(cn=cn)

        placard.signals.group_rename.send(self.object, user=self.user, old_dn=old_dn, old_pk=old_pk)
        return self.object


class EmailForm(LDAPForm):
    subject = fields.CharField(widget=forms.TextInput(attrs={'size': 60}))
    body = fields.CharField(widget=forms.Textarea(attrs={'class': 'vLargeTextField', 'rows': 10, 'cols': 40}))

    def get_data(self):
        return self.cleaned_data['subject'], self.cleaned_data['body']

    def save(self, commit=True):
        placard.signals.group_email.send(self.object, user=self.user, subject=self.cleaned_data['subject'], body=self.cleaned_data['body'])
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
                print ctx
                subject = django.template.Template(subject_t).render(ctx)
                body = django.template.Template(body_t).render(ctx)
                emails.append((subject, body, django.conf.settings.DEFAULT_FROM_EMAIL, [member.mail]))
#        if emails:
#            send_mass_mail(emails)

        return self.object


class DeleteGroupForm(GroupForm):
    """ Delete a group """

    def save(self, commit=True):
        placard.signals.group_delete.send(self.object, user=self.user)

        self.object.delete()

        for _, obj in self.slave_objs:
            obj.delete()

        return None

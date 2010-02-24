from django import forms

from placard.client import LDAPClient

class BasicLDAPGroupForm(forms.Form):
    cn = forms.CharField(label='CN')

    def save(self):
        data = self.cleaned_data
        conn = LDAPClient()
        conn.add_group(**data)


class AddGroupForm(forms.Form):
    add_group = forms.ChoiceField(choices=[('','--------------------')]+[(x.gidNumber, x.name()) for x in LDAPClient().get_groups()])

    def save(self, uid):
        conn = LDAPClient()
        conn.add_group_member(self.cleaned_data['add_group'], uid)

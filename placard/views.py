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

import django.views.generic
import placard.models
import placard.forms
import tldap

from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponseRedirect
from django.core.mail import send_mass_mail
from django.template import RequestContext
from django.core.urlresolvers import reverse

from andsome.util.filterspecs import Filter, FilterBar

def index(request):

    return render_to_response('index.html', locals(), context_instance=RequestContext(request))


def search(request):

    if request.method == 'POST':
        term_list = request.REQUEST['sitesearch'].lower().split(' ')

        user_list = placard.models.account.objects.all()
        group_list = placard.models.group.objects.all()

        for term in term_list:
            if term != "":
                user_list = user_list.filter(tldap.Q(uid__contains=term) | tldap.Q(cn__contains=term))
                group_list = group_list.filter(tldap.Q(cn__contains=term) | tldap.Q(description__contains=term))

        return render_to_response('search.html', locals(), context_instance=RequestContext(request))

    return HttpResponseRedirect(reverse('plac_index'))


def account_photo(request, username):
    account = get_object_or_404(placard.models.account, uid=username)
    if account.jpegPhoto is not None:
        return HttpResponse(account.jpegPhoto, content_type="image/jpeg")
    else:
        return HttpResponseNotFound()


def check_permissions(self, request):
    if len(self.permissions) != 0 or self.login_required:
        if not request.user.is_authenticated():
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.build_absolute_uri())

    if len(self.permissions) == 0:
        return None

    ok = False
    for p in self.permissions:
        if request.user.has_perm(p):
            ok = True

    if not ok:
        return HttpResponseForbidden()

    return None


class ListView(django.views.generic.ListView):
    permissions = []
    login_required = False

    def check_permissions(self, request, kwargs):
        return check_permissions(self, request)

    def dispatch(self, *args, **kwargs):
        r = self.check_permissions(args[0], kwargs)
        if r is not None:
            return r
        return super(ListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['request'] = self.request
        return context


class DetailView(django.views.generic.DetailView):
    permissions = []
    login_required = False

    def check_permissions(self, request, kwargs):
        return check_permissions(self, request)

    def dispatch(self, *args, **kwargs):
        r = self.check_permissions(args[0], kwargs)
        if r is not None:
            return r
        return super(DetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['request'] = self.request
        return context


class FormView(django.views.generic.FormView):
    permissions = []
    login_required = False

    def check_permissions(self, request, kwargs):
        return check_permissions(self, request)

    def dispatch(self, *args, **kwargs):
        r = self.check_permissions(args[0], kwargs)
        if r is not None:
            return r
        return super(FormView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(FormView, self).get_context_data(**kwargs)
        context['request'] = self.request
        return context


class AccountList(ListView):
    model = placard.models.account
    template_name = "lusers/user_list.html"
    context_object_name = "user_list"

    def get_queryset(self):
        request = self.request

        user_list = self.get_default_queryset()

        if request.GET.has_key('group'):
            try:
                group = placard.models.group.objects.get(cn=request.GET['group'])
                user_list = user_list.filter(tldap.Q(primary_group=group) | tldap.Q(secondary_groups=group))
            except  placard.models.group.DoesNotExist:
                pass

        return user_list

    def get_default_queryset(self):
        return placard.models.account.objects.all()

    def get_context_data(self, **kwargs):
        context = super(AccountList, self).get_context_data(**kwargs)
        group_list = {}
        for group in placard.models.group.objects.all():
            group_list[group.cn] = group.cn

        filter_list = []
        filter_list.append(Filter(self.request, 'group', group_list))
        context['filter_bar'] = FilterBar(self.request, filter_list)

        return context


class AccountDetail(DetailView):
    model = placard.models.account
    template_name = "lusers/user_detail.html"
    context_object_name = "luser"

    def get_context_data(self, **kwargs):
        context = super(AccountDetail, self).get_context_data(**kwargs)
        context['form'] = placard.forms.AddGroupForm(account=self.object)
        context['username'] = self.object.uid
        return context

    def get_object(self):
        return get_object_or_404(placard.models.account, uid=self.kwargs['username'])


class AccountVerbose(AccountDetail):
    template_name = "lusers/user_detail_verbose.html"
    permissions = [ 'auth.change_group' ]


class AccountGroups(AccountDetail):
    template_name = "lusers/users_groups.html"
    permissions = [ 'auth.change_group' ]


class AccountGeneric(FormView):
    def get_context_data(self, **kwargs):
        context = super(AccountGeneric, self).get_context_data(**kwargs)
        if 'username' in self.kwargs:
            context['username'] = self.kwargs['username']
            context['luser'] = self.object
        return context

    def get_form_kwargs(self):
        kwargs = super(AccountGeneric, self).get_form_kwargs()
        if 'username' in self.kwargs:
            kwargs['account'] = self.get_object()
            self.object = kwargs['account']
        return kwargs

    def get_object(self):
            return get_object_or_404(placard.models.account, uid=self.kwargs['username'])

    def form_valid(self, form):
        self.object = form.save()
        return super(AccountGeneric, self).form_valid(form)

    def get_success_url(self):
        return reverse("plac_user_detail",kwargs={ 'username': self.object.uid })


class AccountAdd(AccountGeneric):
    template_name = "lusers/user_form.html"
    form_class = placard.forms.LDAPAddUserForm
    permissions = [ 'auth.add_user' ]


class AccountEdit(AccountGeneric):
    template_name = "lusers/user_form.html"
    context_object_name = "luser"
    permissions = [ 'auth.change_user', 'auth.hr_user' ]

    def get_form_class(self):
        request = self.request
        if request.user.has_perm('auth.add_user'):
            return self.get_admin_form_class()
        elif request.user.has_perm('auth.hr_user'):
            return self.get_hr_form_class()
        else:
            raise RuntimeError("Bad permissions")

    def get_admin_form_class(self):
            return placard.forms.LDAPUserForm

    def get_hr_form_class(self):
            return placard.forms.LDAPHrUserForm

class AccountChangePassword(AccountGeneric):
    template_name = "lusers/password_form.html"
    form_class = placard.forms.LDAPAdminPasswordForm
    login_required = True
    permissions = [ "auth.change_user" ]


class UserChangePassword(AccountChangePassword):
    form_class = placard.forms.LDAPPasswordForm
    permissions = []

    def dispatch(self, *args, **kwargs):
        request = args[0]
        if request.user.is_authenticated():
            kwargs['username'] = request.user.username
        return super(UserChangePassword, self).dispatch(*args, **kwargs)


class AccountLock(AccountGeneric):
    template_name = "lusers/user_confirm_lock.html"
    form_class = placard.forms.LockAccountForm
    permissions = [ 'auth.change_user' ]


class AccountUnlock(AccountGeneric):
    template_name = "lusers/user_confirm_unlock.html"
    form_class = placard.forms.UnlockAccountForm
    permissions = [ 'auth.change_user' ]


class AccountAddGroup(AccountGeneric):
    template_name = "lgroups/group_add_member_form.html"
    form_class = placard.forms.AddGroupForm
    permissions = [ 'auth.change_user' ]


class AccountRemoveGroup(AccountGeneric):
    template_name = "lgroups/remove_member.html"
    form_class = placard.forms.RemoveGroupForm
    permissions = [ 'auth.change_user' ]

    def get_context_data(self, **kwargs):
        context = super(AccountRemoveGroup, self).get_context_data(**kwargs)
        context['group'] = self.group
        return context

    def get_form_kwargs(self):
        kwargs = super(AccountRemoveGroup, self).get_form_kwargs()
        kwargs['group'] = get_object_or_404(placard.models.group, cn=self.kwargs['group'])
        self.group = kwargs['group']
        return kwargs


class AccountDelete(AccountGeneric):
    template_name = "lusers/user_confirm_delete.html"
    form_class = placard.forms.DeleteAccountForm
    permissions = [ 'auth.delete_user' ]


class GroupList(ListView):
    model = placard.models.group
    template_name = "lgroups/group_list.html"
    context_object_name = "group_list"


class GroupDetail(DetailView):
    model = placard.models.account
    template_name = "lgroups/group_detail.html"
    context_object_name = "group"

    def get_context_data(self, **kwargs):
        context = super(GroupDetail, self).get_context_data(**kwargs)
        context['form'] = placard.forms.AddMemberForm(group=self.object)
        return context

    def get_object(self):
        return get_object_or_404(placard.models.group, cn=self.kwargs['group'])


class GroupVerbose(GroupDetail):
    template_name = "lgroups/group_detail_verbose.html"


class GroupGeneric(FormView):
    def get_context_data(self, **kwargs):
        context = super(GroupGeneric, self).get_context_data(**kwargs)
        if 'group' in self.kwargs:
            context['group'] = self.object
        return context

    def get_form_kwargs(self):
        kwargs = super(GroupGeneric, self).get_form_kwargs()
        if 'group' in self.kwargs:
            kwargs['group'] = self.get_object()
            self.object = kwargs['group']
        return kwargs

    def get_object(self):
            return get_object_or_404(placard.models.group, cn=self.kwargs['group'])

    def form_valid(self, form):
        self.object = form.save()
        return super(GroupGeneric, self).form_valid(form)

    def get_success_url(self):
        return reverse("plac_grp_detail",kwargs={ 'group': self.object.cn })


class GroupEdit(GroupGeneric):
    template_name = "lgroups/group_form.html"
    form_class = placard.forms.LDAPGroupForm

    def check_permissions(self, request, kwargs):
        if 'group' in kwargs:
            self.permissions = [ 'auth.add_group' ]
        else:
            self.permissions = [ 'auth.change_group' ]
        return super(GroupEdit, self).check_permissions(request, kwargs)


class GroupAddMember(GroupGeneric):
    template_name = "lgroups/group_add_member_form.html"
    form_class = placard.forms.AddMemberForm
    permissions = [ 'auth.change_group' ]


class GroupRemoveMember(GroupGeneric):
    template_name = "lgroups/remove_member.html"
    form_class = placard.forms.RemoveMemberForm
    permissions = [ 'auth.change_group' ]

    def get_context_data(self, **kwargs):
        context = super(GroupRemoveMember, self).get_context_data(**kwargs)
        context['username'] = self.kwargs['username']
        context['luser'] = self.account
        return context

    def get_form_kwargs(self):
        kwargs = super(GroupRemoveMember, self).get_form_kwargs()
        kwargs['account'] = get_object_or_404(placard.models.account, uid=self.kwargs['username'])
        self.account = kwargs['account']
        return kwargs


class GroupRename(GroupGeneric):
    template_name = "lgroups/group_rename.html"
    form_class = placard.forms.RenameGroupForm
    permissions = [ 'auth.change_group' ]


class GroupEmail(GroupGeneric):
    template_name = "lgroups/send_email_form.html"
    form_class = placard.forms.EmailForm


class GroupDelete(GroupGeneric):
    template_name = "lgroups/group_confirm_delete.html"
    form_class = placard.forms.DeleteGroupForm
    permissions = [ 'auth.delete_group' ]

    def get_success_url(self):
        return reverse("plac_grp_list")



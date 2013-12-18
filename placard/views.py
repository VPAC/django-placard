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
import placard.ldap_bonds as bonds
import placard.forms
import placard.filterspecs
import tldap

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.http import Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse


def index(request):

    return render_to_response('placard/index.html', locals(), context_instance=RequestContext(request))


def search(request):

    if request.method == 'GET' and 'q' in request.REQUEST:
        term_list = request.REQUEST['q'].lower().split(' ')
        q = " ".join(term_list)
    else:
        q = ""

    if q != "":

        account_list = bonds.master.accounts()
        group_list = bonds.master.groups()

        for term in term_list:
            if term != "":
                account_list = account_list.filter(tldap.Q(pk__contains=term) | tldap.Q(cn__contains=term) | tldap.Q(description__contains=term))
                group_list = group_list.filter(tldap.Q(pk__contains=term) | tldap.Q(description__contains=term))

    else:

        account_list = []
        group_list = []

    kwargs = {
        'q': q,
        'account_list': account_list,
        'group_list': group_list,
        'request': request,
    }

    return render_to_response('placard/search.html', kwargs, context_instance=RequestContext(request))


def account_photo(request, account):
    account = bonds.master.get_account_or_404(pk=account)
    if account.jpegPhoto is not None:
        return HttpResponse(account.jpegPhoto, content_type="image/jpeg")
    else:
        return HttpResponseNotFound()


class PermissionMixin(object):
    permissions = []
    login_required = False

    def check_permissions(self, request, kwargs):
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
            return HttpResponseForbidden("<h1>Access is Forbidden.</h1>")

        return None


class ListView(PermissionMixin, django.views.generic.ListView):
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['request'] = self.request
        return context

    def dispatch(self, *args, **kwargs):
        r = self.check_permissions(args[0], kwargs)
        if r is not None:
            return r
        return super(ListView, self).dispatch(*args, **kwargs)


class DetailView(PermissionMixin, django.views.generic.DetailView):
    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['request'] = self.request
        return context

    def dispatch(self, *args, **kwargs):
        r = self.check_permissions(args[0], kwargs)
        if r is not None:
            return r
        return super(DetailView, self).dispatch(*args, **kwargs)


class FormView(PermissionMixin, django.views.generic.FormView):
    def get_context_data(self, **kwargs):
        context = super(FormView, self).get_context_data(**kwargs)
        context['request'] = self.request
        return context

    def dispatch(self, *args, **kwargs):
        r = self.check_permissions(args[0], kwargs)
        if r is not None:
            return r
        return super(FormView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(FormView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class AccountMixin(object):
    def get_slave_objs(self):
        objs = []
        for slave_id, bond in bonds.slaves.iteritems():
            try:
                obj = bond.accounts().get(pk=self.object.pk)
                objs.append((bond, obj))
            except bond.AccountDoesNotExist:
                pass
        return objs

    def create_slave_objs(self):
        objs = []
        for slave_id, bond in bonds.slaves.iteritems():
            obj = bond.create_account()
            obj.set_defaults()
            objs.append((bond, obj))
        return objs


class AccountList(ListView, AccountMixin):
    template_name = "placard/account_list.html"
    context_object_name = "account_list"

    def get_queryset(self):
        request = self.request

        account_list = self.get_default_queryset()

        if request.GET.has_key('group'):
            try:
                group = bonds.master.groups().get(cn=request.GET['group'])
                account_list = account_list.filter(tldap.Q(primary_group=group) | tldap.Q(secondary_groups=group))
            except bonds.master.GroupDoesNotExist:
                pass

        if request.GET.has_key('exclude'):
            try:
                group = bonds.master.groups().get(cn=request.GET['exclude'])
                account_list = account_list.filter(~(tldap.Q(primary_group=group) | tldap.Q(secondary_groups=group)))
            except bonds.master.GroupDoesNotExist:
                pass

        return account_list

    def get_default_queryset(self):
        return bonds.master.accounts()

    def get_context_data(self, **kwargs):
        context = super(AccountList, self).get_context_data(**kwargs)
        group_list = {}
        for group in bonds.master.groups():
            group_list[group.cn] = group.cn

        filter_list = []
        filter_list.append(placard.filterspecs.Filter(self.request, 'group', group_list, "Include"))
        filter_list.append(placard.filterspecs.Filter(self.request, 'exclude', group_list, "Exclude"))
        context['filter_bar'] = placard.filterspecs.FilterBar(self.request, filter_list)

        return context


class AccountDetail(DetailView, AccountMixin):
    template_name = "placard/account_detail.html"
    context_object_name = "account"

    def get_context_data(self, **kwargs):
        context = super(AccountDetail, self).get_context_data(**kwargs)
        master_obj = bonds.master, self.object
        slave_objs = self.get_slave_objs()
        context['form'] = placard.forms.AddGroupForm(user=self.request.user, master_obj=master_obj, slave_objs=slave_objs)
        context['slave_objs'] = slave_objs
        context['master_bond'] = bonds.master
        context['account_bond'] = self.account_bond
        context['is_slave'] = self.account_bond.slave_id is not None
        return context

    def get_object(self):
        if 'slave' in self.kwargs:
            slave_id = self.kwargs['slave']
            try:
                bond = bonds.slaves[slave_id]
            except KeyError:
                raise Http404("Invalid slave given")
        else:
            bond = bonds.master

        self.account_bond = bond
        return bond.get_account_or_404(pk=self.kwargs['account'])


class AccountVerbose(AccountDetail, AccountMixin):
    template_name = "placard/account_detail_verbose.html"


class AccountGeneric(FormView, AccountMixin):
    def get_context_data(self, **kwargs):
        context = super(AccountGeneric, self).get_context_data(**kwargs)
        context['account'] = self.object
        context['created'] = self.created
        return context

    def get_form_kwargs(self):
        kwargs = super(AccountGeneric, self).get_form_kwargs()
        if 'account' in self.kwargs:
            self.object = self.get_object()
            kwargs['master_obj'] = bonds.master, self.object
            kwargs['slave_objs'] = self.get_slave_objs()
            kwargs['created'] = False
        else:
            self.object = self.create_object()
            kwargs['master_obj'] = bonds.master, self.object
            kwargs['slave_objs'] = self.create_slave_objs()
            kwargs['created'] = True
        self.created = kwargs['created']
        return kwargs

    def get_object(self):
        return bonds.master.get_account_or_404(pk=self.kwargs['account'])

    def create_object(self):
        obj = bonds.master.create_account()
        obj.set_defaults()
        return obj

    def form_valid(self, form):
        self.object = form.save()
        return super(AccountGeneric, self).form_valid(form)

    def get_success_url(self):
        return reverse("plac_account_detail", kwargs={'account': self.object.pk})


class AccountAdd(AccountGeneric):
    template_name = "placard/account_form.html"
    form_class = placard.forms.LDAPAddAccountForm
    permissions = ['placard.add_account']


class AccountEdit(AccountGeneric):
    template_name = "placard/account_form.html"
    context_object_name = "account"
    permissions = ['placard.change_account', 'placard.hr_change_account']

    def get_form_class(self):
        request = self.request
        if 'account' not in self.kwargs:
            raise RuntimeError("Username parameter is required")
        elif request.user.has_perm('placard.change_account'):
            return self.get_admin_form_class()
        elif request.user.has_perm('placard.hr_change_account'):
            return self.get_hr_form_class()
        else:
            raise RuntimeError("Bad permissions")

    def get_admin_form_class(self):
            return placard.forms.LDAPAccountForm

    def get_hr_form_class(self):
            return placard.forms.LDAPHrAccountForm


class AccountChangePassword(AccountGeneric):
    template_name = "placard/password_form.html"
    form_class = placard.forms.LDAPAdminPasswordForm
    login_required = True
    permissions = ["placard.change_account_password"]


class ChangePassword(AccountChangePassword):
    form_class = placard.forms.LDAPPasswordForm
    permissions = []

    def dispatch(self, *args, **kwargs):
        request = args[0]
        if request.user.is_authenticated():
            kwargs['account'] = request.user.username
        self.kwargs = kwargs
        return super(ChangePassword, self).dispatch(*args, **kwargs)


class AccountLock(AccountGeneric):
    template_name = "placard/account_confirm_lock.html"
    form_class = placard.forms.LockAccountForm
    permissions = ['placard.lock_account']


class AccountUnlock(AccountGeneric):
    template_name = "placard/account_confirm_unlock.html"
    form_class = placard.forms.UnlockAccountForm
    permissions = ['placard.lock_account']


class AccountAddGroup(AccountGeneric):
    template_name = "placard/group_add_member_form.html"
    form_class = placard.forms.AddGroupForm
    permissions = ['placard.change_account']


class AccountRemoveGroup(AccountGeneric):
    template_name = "placard/remove_member.html"
    form_class = placard.forms.RemoveGroupForm
    permissions = ['placard.change_account']

    def get_context_data(self, **kwargs):
        context = super(AccountRemoveGroup, self).get_context_data(**kwargs)
        context['group'] = self.group
        return context

    def get_form_kwargs(self):
        kwargs = super(AccountRemoveGroup, self).get_form_kwargs()
        kwargs['group'] = bonds.master.get_group_or_404(cn=self.kwargs['group'])
        self.group = kwargs['group']
        return kwargs


class AccountDelete(AccountGeneric):
    template_name = "placard/account_confirm_delete.html"
    form_class = placard.forms.DeleteAccountForm
    permissions = ['placard.delete_account']

    def get_success_url(self):
        return reverse("plac_account_list")


class GroupMixin(object):
    def get_slave_objs(self):
        objs = []
        for slave_id, bond in bonds.slaves.iteritems():
            try:
                obj = bond.groups().get(pk=self.object.pk)
                objs.append((bond, obj))
            except bond.GroupDoesNotExist:
                pass
        return objs

    def create_slave_objs(self):
        objs = []
        for slave_id, bond in bonds.slaves.iteritems():
            obj = bond.create_group()
            obj.set_defaults()
            objs.append((bond, obj))
        return objs


class GroupList(ListView, GroupMixin):
    template_name = "placard/group_list.html"
    context_object_name = "group_list"

    def get_queryset(self):
        return bonds.master.groups()


class GroupDetail(DetailView, GroupMixin):
    template_name = "placard/group_detail.html"
    context_object_name = "group"

    def get_context_data(self, **kwargs):
        context = super(GroupDetail, self).get_context_data(**kwargs)
        master_obj = bonds.master, self.object
        slave_objs = self.get_slave_objs()
        context['form'] = placard.forms.AddMemberForm(user=self.request.user, master_obj=master_obj, slave_objs=slave_objs)
        context['slave_objs'] = slave_objs
        context['master_bond'] = bonds.master
        context['group_bond'] = self.group_bond
        context['is_slave'] = self.group_bond.slave_id is not None
        return context

    def get_object(self):
        if 'slave' in self.kwargs:
            slave_id = self.kwargs['slave']
            try:
                bond = bonds.slaves[slave_id]
            except KeyError:
                raise Http404("Invalid slave given")
        else:
            bond = bonds.master

        self.group_bond = bond
        return bond.get_group_or_404(pk=self.kwargs['group'])


class GroupVerbose(GroupDetail, GroupMixin):
    template_name = "placard/group_detail_verbose.html"


class GroupGeneric(FormView, GroupMixin):
    def get_context_data(self, **kwargs):
        context = super(GroupGeneric, self).get_context_data(**kwargs)
        context['group'] = self.object
        context['created'] = self.created
        return context

    def get_form_kwargs(self):
        kwargs = super(GroupGeneric, self).get_form_kwargs()
        if 'group' in self.kwargs:
            self.object = self.get_object()
            kwargs['master_obj'] = bonds.master, self.object
            kwargs['slave_objs'] = self.get_slave_objs()
            kwargs['created'] = False
        else:
            self.object = self.create_object()
            kwargs['master_obj'] = bonds.master, self.object
            kwargs['slave_objs'] = self.create_slave_objs()
            kwargs['created'] = True
        self.created = kwargs['created']
        return kwargs

    def get_object(self):
        return bonds.master.get_group_or_404(cn=self.kwargs['group'])

    def create_object(self):
        obj = bonds.master.create_group()
        obj.set_defaults()
        return obj

    def form_valid(self, form):
        self.object = form.save()
        return super(GroupGeneric, self).form_valid(form)

    def get_success_url(self):
        return reverse("plac_group_detail", kwargs={'group': self.object.cn})


class GroupEdit(GroupGeneric):
    template_name = "placard/group_form.html"
    form_class = placard.forms.LDAPGroupForm

    def check_permissions(self, request, kwargs):
        if 'group' not in kwargs:
            self.permissions = ['placard.add_group']
        else:
            self.permissions = ['placard.change_group']
        return super(GroupEdit, self).check_permissions(request, kwargs)


class GroupAddMember(GroupGeneric):
    template_name = "placard/group_add_member_form.html"
    form_class = placard.forms.AddMemberForm
    permissions = ['placard.change_group']


class GroupRemoveMember(GroupGeneric):
    template_name = "placard/remove_member.html"
    form_class = placard.forms.RemoveMemberForm
    permissions = ['placard.change_group']

    def get_context_data(self, **kwargs):
        context = super(GroupRemoveMember, self).get_context_data(**kwargs)
        context['account'] = self.account
        return context

    def get_form_kwargs(self):
        kwargs = super(GroupRemoveMember, self).get_form_kwargs()
        kwargs['account'] = bonds.master.get_account_or_404(pk=self.kwargs['account'])
        self.account = kwargs['account']
        return kwargs


class GroupRename(GroupGeneric):
    template_name = "placard/group_rename.html"
    form_class = placard.forms.RenameGroupForm
    permissions = ['placard.rename_group']


class GroupEmail(GroupGeneric):
    template_name = "placard/send_email_form.html"
    form_class = placard.forms.EmailForm
    permissions = ['placard.email_group']


class GroupDelete(GroupGeneric):
    template_name = "placard/group_confirm_delete.html"
    form_class = placard.forms.DeleteGroupForm
    permissions = ['placard.delete_group']

    def get_success_url(self):
        return reverse("plac_group_list")

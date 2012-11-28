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
import placard.filterspecs
import tldap

from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden, HttpResponseRedirect
from django.http import Http404
from django.core.mail import send_mass_mail
from django.template import RequestContext
from django.core.urlresolvers import reverse

def index(request):

    return render_to_response('index.html', locals(), context_instance=RequestContext(request))


def search(request):

    if request.method == 'POST':
        term_list = request.REQUEST['sitesearch'].lower().split(' ')

        user_list = placard.models.account.objects.all()
        group_list = placard.models.group.objects.all()

        for term in term_list:
            if term != "":
                user_list = user_list.filter(tldap.Q(pk__contains=term) | tldap.Q(cn__contains=term) | tldap.Q(description__contains=term))
                group_list = group_list.filter(tldap.Q(pk__contains=term) | tldap.Q(description__contains=term))

        return render_to_response('search.html', locals(), context_instance=RequestContext(request))

    return HttpResponseRedirect(reverse('plac_index'))


def account_photo(request, username):
    account = get_object_or_404(placard.models.account, pk=username)
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
            return HttpResponseForbidden()

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
        objs = {}
        for slave_id, module in placard.models.get_slave_modules().iteritems():
            try:
                obj = module.account.objects.using(slave_id).get(pk=self.object.pk)
                objs[slave_id] = obj
            except module.account.DoesNotExist:
                pass
        return objs


class AccountList(ListView, AccountMixin):
    model = placard.models.account
    template_name = "placard/user_list.html"
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

        if request.GET.has_key('exclude'):
            try:
                group = placard.models.group.objects.get(cn=request.GET['exclude'])
                user_list = user_list.filter(~(tldap.Q(primary_group=group) | tldap.Q(secondary_groups=group)))
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
        filter_list.append(placard.filterspecs.Filter(self.request, 'group', group_list, "Include"))
        filter_list.append(placard.filterspecs.Filter(self.request, 'exclude', group_list, "Exclude"))
        context['filter_bar'] = placard.filterspecs.FilterBar(self.request, filter_list)

        return context


class AccountDetail(DetailView, AccountMixin):
    model = placard.models.account
    template_name = "placard/user_detail.html"
    context_object_name = "luser"

    def get_context_data(self, **kwargs):
        context = super(AccountDetail, self).get_context_data(**kwargs)
        slave_objs = self.get_slave_objs()
        context['form'] = placard.forms.AddGroupForm(user=self.request.user, slave_objs=slave_objs, account=self.object)
        context['slave_objs'] = slave_objs
        if 'slave' in self.kwargs:
            context['slave_id'] = self.kwargs['slave']
        return context

    def get_object(self):
        if 'slave' in self.kwargs:
            slave_id = self.kwargs['slave']
            model = placard.models.get_slave_module_by_id(slave_id).account
        else:
            slave_id = None
            model = placard.models.account

        try:
            return model.objects.using(slave_id).get(pk=self.kwargs['username'])
        except model.DoesNotExist:
            raise Http404


class AccountVerbose(AccountDetail, AccountMixin):
    template_name = "placard/user_detail_verbose.html"


class AccountGroups(AccountDetail, AccountMixin):
    template_name = "placard/users_groups.html"


class AccountGeneric(FormView, AccountMixin):
    def get_context_data(self, **kwargs):
        context = super(AccountGeneric, self).get_context_data(**kwargs)
        if 'username' in self.kwargs:
            context['luser'] = self.object
        return context

    def get_form_kwargs(self):
        kwargs = super(AccountGeneric, self).get_form_kwargs()
        if 'username' in self.kwargs:
            kwargs['account'] = self.get_object()
            self.object = kwargs['account']
            kwargs['slave_objs'] = self.get_slave_objs()
        return kwargs

    def get_object(self):
            return get_object_or_404(placard.models.account, pk=self.kwargs['username'])

    def form_valid(self, form):
        self.object = form.save()
        return super(AccountGeneric, self).form_valid(form)

    def get_success_url(self):
        return reverse("plac_user_detail",kwargs={ 'username': self.object.pk })


class AccountAdd(AccountGeneric):
    template_name = "placard/user_form.html"
    form_class = placard.forms.LDAPAddUserForm
    permissions = [ 'placard.add_account' ]


class AccountEdit(AccountGeneric):
    template_name = "placard/user_form.html"
    context_object_name = "luser"
    permissions = [ 'placard.change_account', 'placard.hr_change_account' ]

    def get_form_class(self):
        request = self.request
        if 'username' not in self.kwargs:
            raise RuntimeError("Username parameter is required")
        elif request.user.has_perm('placard.change_account'):
            return self.get_admin_form_class()
        elif request.user.has_perm('placard.hr_change_account'):
            return self.get_hr_form_class()
        else:
            raise RuntimeError("Bad permissions")

    def get_admin_form_class(self):
            return placard.forms.LDAPUserForm

    def get_hr_form_class(self):
            return placard.forms.LDAPHrUserForm


class AccountChangePassword(AccountGeneric):
    template_name = "placard/password_form.html"
    form_class = placard.forms.LDAPAdminPasswordForm
    login_required = True
    permissions = [ "placard.change_account_password" ]


class UserChangePassword(AccountChangePassword):
    form_class = placard.forms.LDAPPasswordForm
    permissions = []

    def dispatch(self, *args, **kwargs):
        request = args[0]
        if request.user.is_authenticated():
            kwargs['username'] = request.user.username
        return super(UserChangePassword, self).dispatch(*args, **kwargs)


class AccountLock(AccountGeneric):
    template_name = "placard/user_confirm_lock.html"
    form_class = placard.forms.LockAccountForm
    permissions = [ 'placard.lock_account' ]


class AccountUnlock(AccountGeneric):
    template_name = "placard/user_confirm_unlock.html"
    form_class = placard.forms.UnlockAccountForm
    permissions = [ 'placard.lock_account' ]


class AccountAddGroup(AccountGeneric):
    template_name = "placard/group_add_member_form.html"
    form_class = placard.forms.AddGroupForm
    permissions = [ 'placard.change_account' ]


class AccountRemoveGroup(AccountGeneric):
    template_name = "placard/remove_member.html"
    form_class = placard.forms.RemoveGroupForm
    permissions = [ 'placard.change_account' ]

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
    template_name = "placard/user_confirm_delete.html"
    form_class = placard.forms.DeleteAccountForm
    permissions = [ 'placard.delete_account' ]

    def get_success_url(self):
        return reverse("plac_user_list")


class GroupMixin(object):
    def get_slave_objs(self):
        objs = {}
        for slave_id, module in placard.models.get_slave_modules().iteritems():
            try:
                obj = module.group.objects.using(slave_id).get(pk=self.object.pk)
                objs[slave_id] = obj
            except module.group.DoesNotExist:
                pass
        return objs


class GroupList(ListView, GroupMixin):
    model = placard.models.group
    template_name = "placard/group_list.html"
    context_object_name = "group_list"


class GroupDetail(DetailView, GroupMixin):
    model = placard.models.account
    template_name = "placard/group_detail.html"
    context_object_name = "group"

    def get_context_data(self, **kwargs):
        context = super(GroupDetail, self).get_context_data(**kwargs)
        slave_objs = self.get_slave_objs()
        context['form'] = placard.forms.AddMemberForm(user=self.request.user, slave_objs=slave_objs, group=self.object)
        context['slave_objs'] = slave_objs
        if 'slave' in self.kwargs:
            context['slave_id'] = self.kwargs['slave']
        return context

    def get_object(self):
        if 'slave' in self.kwargs:
            slave_id = self.kwargs['slave']
            model = placard.models.get_slave_module_by_id(slave_id).group
        else:
            slave_id = None
            model = placard.models.group

        try:
            return model.objects.using(slave_id).get(pk=self.kwargs['group'])
        except model.DoesNotExist:
            raise Http404


class GroupVerbose(GroupDetail, GroupMixin):
    template_name = "placard/group_detail_verbose.html"


class GroupGeneric(FormView, GroupMixin):
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
            kwargs['slave_objs'] = self.get_slave_objs()
        return kwargs

    def get_object(self):
            return get_object_or_404(placard.models.group, cn=self.kwargs['group'])

    def form_valid(self, form):
        self.object = form.save()
        return super(GroupGeneric, self).form_valid(form)

    def get_success_url(self):
        return reverse("plac_grp_detail",kwargs={ 'group': self.object.cn })


class GroupEdit(GroupGeneric):
    template_name = "placard/group_form.html"
    form_class = placard.forms.LDAPGroupForm

    def check_permissions(self, request, kwargs):
        if 'group' not in kwargs:
            self.permissions = [ 'placard.add_group' ]
        else:
            self.permissions = [ 'placard.change_group' ]
        return super(GroupEdit, self).check_permissions(request, kwargs)


class GroupAddMember(GroupGeneric):
    template_name = "placard/group_add_member_form.html"
    form_class = placard.forms.AddMemberForm
    permissions = [ 'placard.change_group' ]


class GroupRemoveMember(GroupGeneric):
    template_name = "placard/remove_member.html"
    form_class = placard.forms.RemoveMemberForm
    permissions = [ 'placard.change_group' ]

    def get_context_data(self, **kwargs):
        context = super(GroupRemoveMember, self).get_context_data(**kwargs)
        context['luser'] = self.account
        return context

    def get_form_kwargs(self):
        kwargs = super(GroupRemoveMember, self).get_form_kwargs()
        kwargs['account'] = get_object_or_404(placard.models.account, pk=self.kwargs['username'])
        self.account = kwargs['account']
        return kwargs


class GroupRename(GroupGeneric):
    template_name = "placard/group_rename.html"
    form_class = placard.forms.RenameGroupForm
    permissions = [ 'placard.rename_group' ]


class GroupEmail(GroupGeneric):
    template_name = "placard/send_email_form.html"
    form_class = placard.forms.EmailForm
    permissions = [ 'placard.email_group' ]


class GroupDelete(GroupGeneric):
    template_name = "placard/group_confirm_delete.html"
    form_class = placard.forms.DeleteGroupForm
    permissions = [ 'placard.delete_group' ]

    def get_success_url(self):
        return reverse("plac_grp_list")



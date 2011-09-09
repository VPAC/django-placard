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


from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden
from django.contrib.auth.decorators import permission_required, login_required
from django.core.urlresolvers import reverse
from django.contrib import messages

from andsome.util.filterspecs import Filter, FilterBar

from placard.client import LDAPClient
from placard import exceptions
from placard.lgroups.forms import AddGroupForm
from placard.lusers.forms import BasicLDAPUserForm, LDAPAdminPasswordForm, LDAPPasswordForm

def user_list(request, default_filter=None):
    conn = LDAPClient()
    if request.REQUEST.has_key('group'):
        user_list = conn.get_group_members("gidNumber=%s" % request.GET['group'])
    else:
        if default_filter:
            user_list = conn.get_users(default_filter)
        else:
            user_list = conn.get_users()

    if request.REQUEST.has_key('q'):
        term_list = request.REQUEST['q'].lower().split(' ')
        user_list = conn.search_users(term_list)

    filter_list = []
    group_list = {}
    for group in conn.get_groups():
        group_list[group.gidNumber] = group.cn

    filter_list.append(Filter(request, 'group', group_list))
    filter_bar = FilterBar(request, filter_list)

    return render_to_response('lusers/user_list.html', locals(), context_instance=RequestContext(request))


def user_detail(request, username):
    conn = LDAPClient()
    try:
        luser = conn.get_user("uid=%s" % username)
    except exceptions.DoesNotExistException:
        raise Http404

    if request.method == 'POST':
        form = AddGroupForm(request.POST)
        if form.is_valid():
            group_id = form.save(username)
            group = conn.get_group('gidNumber=%s' % group_id)
            messages.info(request, 'User %s has been added to group %s.' % (username, group)) 
            return HttpResponseRedirect(luser.get_absolute_url())
    else:
        form = AddGroupForm()

    return render_to_response('lusers/user_detail.html', locals(), context_instance=RequestContext(request))


def add_edit_user(request, username=None, form=BasicLDAPUserForm, template_name='lusers/user_form.html'):
    UserForm = form

    if (request.user.username != username) and (not request.user.has_perm('auth.add_user')):
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            if username:
                ldap_user = form.save(username)
            else:
                ldap_user = form.save()
            return HttpResponseRedirect(ldap_user.get_absolute_url())
    else:
        if username:
            form = UserForm()
            conn = LDAPClient()
            ldap_user = conn.get_user("uid=%s" % username)
            form.initial = ldap_user.__dict__
        else:
            form = UserForm()
    
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
 

@login_required
def user_edit(request, form, template_name):

    return add_edit_user(request, request.user.username, form, template_name)
    

@login_required
def change_password(request, username, password_form=LDAPAdminPasswordForm, template='lusers/password_form.html', redirect_url=None):

    if (request.user.username != username) and (not request.user.has_perm('auth.change_user')):
        return HttpResponseForbidden()

    PasswordForm = password_form

    if request.method == 'POST':
        
        form = PasswordForm(request.POST)
        if form.is_valid():
            form.save(username)
            messages.info(request,'Password changed successfully')
            if redirect_url:
                return HttpResponseRedirect(redirect_url)
            return HttpResponseRedirect(reverse('plac_user_detail', args=[username]))              
    else:
        form = PasswordForm()

    return render_to_response(template, locals(), context_instance=RequestContext(request))

@login_required
def user_password_change(request, redirect_url=None):

    return change_password(request, request.user.username, LDAPPasswordForm, 'lusers/user_password_form.html', redirect_url)

@permission_required('auth.delete_user')
def delete_user(request, username):

    if request.method == 'POST':
        conn = LDAPClient()
        conn.delete_user('uid=%s' % username)
        return HttpResponseRedirect(reverse('plac_user_list'))
    
    return render_to_response('lusers/user_confirm_delete.html', locals(), context_instance=RequestContext(request))


@permission_required('auth.change_user')
def lock_user(request, username):
    conn = LDAPClient()
    conn.lock_user('uid=%s' % username)
    messages.info(request, "%s's has been locked" % username)
    luser = conn.get_user('uid=%s' % username)
    return HttpResponseRedirect(luser.get_absolute_url())

@permission_required('auth.change_user')
def unlock_user(request, username):
    conn = LDAPClient()
    conn.unlock_user('uid=%s' % username)
    messages.info(request, "%s's has been unlocked" % username)
    luser = conn.get_user('uid=%s' % username)
    return HttpResponseRedirect(luser.get_absolute_url())

@permission_required('auth.change_user')
def user_detail_verbose(request, username):
    conn = LDAPClient()
    try:
        luser = conn.ldap_search(settings.LDAP_USER_BASE, 'uid=%s' % username)[0]
    except:
        raise Http404
    dn = luser[0]
    luser = luser[1]
    try:
        del(luser['jpegPhoto'])
    except:
        pass
    luser = luser.items()
    return render_to_response('lusers/user_detail_verbose.html', locals(), context_instance=RequestContext(request))

@permission_required('auth.change_user')   
def users_groups(request, username):
    conn = LDAPClient()
    try:
        luser = conn.get_user('uid=%s' % username)
    except:
        raise Http404

    return render_to_response('lusers/users_groups.html', {'luser': luser}, context_instance=RequestContext(request))

    

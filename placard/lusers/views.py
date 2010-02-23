from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseNotFound, Http404
from django.contrib.auth.decorators import permission_required, login_required
from django.core.urlresolvers import reverse

from django_common.util.filterspecs import Filter, FilterBar

from placard import LDAPClient
from placard import exceptions
from placard.lgroups.forms import AddGroupForm
from placard.lusers.forms import BasicLDAPUserForm

def user_list(request):
    conn = LDAPClient()
    if request.REQUEST.has_key('group'):
        group_id = str(request.GET['group'])
        user_list = conn.get_group_members("gidNumber=%s" % group_id)
    else:
        user_list = conn.get_users()

    if request.REQUEST.has_key('q'):
        siteterms = request.REQUEST['q'].lower()
        term_list = siteterms.split(' ')
        user_list = conn.search_users(term_list)

    filter_list = []
    group_list = {}
    for x in conn.get_groups():
        group_list[x.gidNumber] = x.name()

    filter_list.append(Filter(request, 'group', group_list))
    filter_bar = FilterBar(request, filter_list)


    return render_to_response('lusers/user_list.html', locals(), context_instance=RequestContext(request))


def user_detail(request, username):
    conn = LDAPClient()
    try:
        luser = conn.get_user("uid=%s" % username)
    except exceptions.DoesNotExistException:
        return HttpResponseNotFound()

    if request.method == 'POST':
        form = AddGroupForm(request.POST)
        if form.is_valid():
            form.save(username)
            return HttpResponseRedirect(luser.get_absolute_url())

    else:
        form = AddGroupForm()

    return render_to_response('lusers/user_detail.html', locals(), context_instance=RequestContext(request))


def add_edit_user(request, username=None, form=BasicLDAPUserForm):
    UserForm = form

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
    
    return render_to_response('lusers/user_form.html', locals(), context_instance=RequestContext(request))

 
add_edit_user = permission_required('auth.add_user')(add_edit_user)


def change_password(request, username):

    if request.method == 'POST':
        
        form = LDAPAdminPasswordForm(request.POST)

        if form.is_valid():
            form.save(username)
            
            return HttpResponseRedirect(reverse('plac_user_detail', args=[username]))
                
    else:

        form = LDAPAdminPasswordForm()

    return render_to_response('lusers/password_form.html', locals(), context_instance=RequestContext(request))

change_password = permission_required('auth.delete_user')(change_password)

@login_required
def user_password_change(request, redirect_url=None):

    user = request.user
    
    if request.method == 'POST':
        
        form = LDAPPasswordForm(request.POST)

        if form.is_valid():
            form.save(user.username)
            request.user.message_set.create(message='Password changed successfully')
            if redirect_url:
                return HttpResponseRedirect(redirect_url)
            return HttpResponseRedirect(reverse('plac_user_detail', args=[user.username]))
                
    else:

        form = LDAPPasswordForm()

        return render_to_response('lusers/user_password_form.html', locals(), context_instance=RequestContext(request))


def delete_user(request, username):

    if request.method == 'POST':
        conn = LDAPClient()
        conn.delete_user('uid=%s' % username)
        return HttpResponseRedirect(reverse('plac_user_list'))
    
    
    return render_to_response('lusers/user_confirm_delete.html', locals(), context_instance=RequestContext(request))

delete_user = permission_required('auth.delete_user')(delete_user)

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

user_detail_verbose = permission_required('auth.delete_user')(user_detail_verbose)

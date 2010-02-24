from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth.decorators import permission_required
from placard.lusers.forms import AddMemberForm

from placard import LDAPClient
from placard.lgroups.forms import BasicLDAPGroupForm
from placard import exceptions

def group_list(request):
    conn = LDAPClient()
    groups = conn.get_groups()

    return render_to_response('lgroups/group_list.html', {'group_list': groups, 'request', request }, context_instance=RequestContext(request))


def group_detail(request, group_id):
    conn = LDAPClient()
    try:
        group = conn.get_group("gidNumber=%s" % group_id)
    except exceptions.DoesNotExistException:
        return HttpResponseNotFound()

    if request.method == 'POST':
        # add member
        form = AddMemberForm(request.POST)
        if form.is_valid():
            form.save(group.gidNumber)
            return HttpResponseRedirect(group.get_absolute_url())
    else:
        form = AddMemberForm()

    member_list = conn.get_group_members("gidNumber=%s" % group_id)

    return render_to_response('lgroups/group_detail.html', locals(), context_instance=RequestContext(request))


def remove_member(request, group_id, user_id):
    conn = LDAPClient()
    try:
        group = conn.get_group("gidNumber=%s" % group_id)
    except exceptions.DoesNotExistException:
        return HttpResponseNotFound()

    if request.method == 'POST':
        conn.remove_group_member(group_id, user_id)
        return HttpResponseRedirect(group.get_absolute_url())

    return render_to_response('lgroups/remove_member.html', locals(), context_instance=RequestContext(request))

remove_member = permission_required('auth.change_group')(remove_member)


def add_edit_group(request, group_id=None, form=BasicLDAPGroupForm):
    Form = form

    if request.method == 'POST':

        form = Form(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('plac_grp_list'))

    else:
        form = Form()

    return render_to_response('lgroups/group_form.html', locals(), context_instance=RequestContext(request))
   
 
def delete_group(request, group_id):
    conn = LDAPClient()
    try:
        group = conn.get_group("gidNumber=%s" % group_id)
    except exceptions.DoesNotExistException:
        return HttpResponseNotFound()

    if request.method == 'POST':
        conn.delete_group(group_id)
        return HttpResponseRedirect(reverse('plac_grp_list'))
    
    return render_to_response('lgroups/group_confirm_delete.html.html', locals(), context_instance=RequestContext(request))


def group_detail_verbose(request, group_id):
    conn = LDAPClient()
    lgroup = conn.ldap_search(settings.LDAP_GROUP_BASE, 'gidNumber=%s' % group_id)[0]
 
    dn = lgroup[0]
    lgroup = lgroup[1].items()
    
    return render_to_response('lgroups/group_detail_verbose.html', locals(), context_instance=RequestContext(request))

group_detail_verbose = permission_required('auth.delete_group')(group_detail_verbose)

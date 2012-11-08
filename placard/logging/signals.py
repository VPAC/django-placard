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

import placard.signals
from placard.logging.models import LogEntry

log = LogEntry.objects.log_action

def account_add(sender, user, **kwargs):
    account = sender
    log(user, account, "A", u"Added account" )

def account_edit(sender, user, data, **kwargs):
    account = sender
    for key,value in data.iteritems():
        old_value = getattr(account, key)
        if key == "primary_group" and old_value is not None:
            old_value = old_value.get_obj()
        if key == "managed_by" and old_value is not None:
            old_value = old_value.get_obj()
        if old_value != value:
            log(user, account, "C", u"Changed '%s' from '%s' to '%s'" % (key, old_value, value) )

def account_password_change(sender, user, **kwargs):
    account = sender
    log(user, account, "C", u"Changed password" )

def account_lock(sender, user, **kwargs):
    account = sender
    log(user, account, "C", u"Locked account" )

def account_unlock(sender, user, **kwargs):
    account = sender
    log(user, account, "C", u"Unlocked account" )

def account_delete(sender, user, **kwargs):
    account = sender
    log(user, account, "D", u"Deleted account" )

def group_add(sender, user, **kwargs):
    group = sender
    log(user, group, "A", u"Added group" )

def group_edit(sender, user, data, **kwargs):
    group = sender
    for key,value in data.iteritems():
        old_value = getattr(group, key)
        if old_value != value:
            log(user, group, "C", u"Changed '%s' from '%s' to '%s'" % (key, old_value, value) )

def group_add_member(sender, user, account, **kwargs):
    group = sender
    log(user, account, "C", u"Added to group '%s'" % group )
    log(user, group, "C", u"Added '%s' to group" % account )

def group_remove_member(sender, user, account, **kwargs):
    group = sender
    log(user, account, "C", u"Removed from group '%s'" % group )
    log(user, group, "C", u"Removed '%s' from group" % account )

def group_delete(sender, user, **kwargs):
    group = sender
    log(user, group, "D", u"Deleted group" )

def group_rename(sender, user, old_dn, old_pk, **kwargs):
    group = sender
    LogEntry.objects.filter(object_dn=old_dn).update(object_dn=group.dn, object_pk=group.pk)
    log(user, group, "C", u"Renamed group from '%s' to '%s'" % (old_pk, group.pk) )

def group_email(sender, user, subject, body, **kwargs):
    group = sender
    log(user, group, "T", u"E-Mailed group" )


def connect_all():
    functions = [
        "account_add",
        "account_edit",
        "account_password_change",
        "account_lock",
        "account_unlock",
        "account_delete",
        "group_add",
        "group_edit",
        "group_add_member",
        "group_remove_member",
        "group_delete",
        "group_rename",
        "group_email",
    ]

    for name in functions:
        f = globals().get(name)
        signal = getattr(placard.signals, name)

        uid = "logging_%s" % name
        signal.connect(f, dispatch_uid=uid)

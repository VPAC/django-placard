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


from django.contrib.auth.middleware import RemoteUserMiddleware
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.contrib import auth

import placard.models
import tldap.transaction

class LDAPRemoteUserMiddleware(RemoteUserMiddleware):
    """
    Middleware for utilizing web-server-provided authentication.
    
    If request.user is not authenticated, then this middleware attempts to
    authenticate the username passed in the ``REMOTE_USER`` request header.
    If authentication is successful, the user is automatically logged in to
    persist the user in the session. 

    If the user doesn't exist the middleware will create a new User object 
    based on information pulled from LDAP
    """

    def process_request(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The placard remote LDAP user auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the RemoteUserMiddleware class.")
        try:
            username = request.META[self.header]
        except KeyError:
            # If specified header doesn't exist then return (leaving
            # request.user set to AnonymousUser by the
            # AuthenticationMiddleware).
            return
        # If the user is already authenticated and that user is the user we are
        # getting passed in the headers, then the correct user is already
        # persisted in the session and we don't need to continue.
        if request.user.is_authenticated():
            if request.user.username == self.clean_username(username, request):
                return
        # We are seeing this user for the first time in this session, attempt
        # to authenticate the user.
        try:
            user = User.objects.get(username__exact=username)
        except User.DoesNotExist:
            # Create user
            ldap_user = placard.models.account.objects.get(pk=username)
            user = User.objects.create_user(ldap_user.pk, ldap_user.mail)
            user.first_name = ldap_user.givenName
            user.last_name = ldap_user.sn
            user.save()
    
        # User is valid.  Set request.user and persist user in the session
        # by logging the user in.
        user.backend = 'placard.backends.LDAPBackend'
        request.user = user
        auth.login(request, user)


class TransactionMiddleware(object):
    """
    Transaction middleware. If this is enabled, each view function will be run
    with commit_on_response activated - that way a save() doesn't do a direct
    commit, the commit is done when a successful response is created. If an
    exception happens, the database is rolled back.
    """
    def process_request(self, request):
        """Enters transaction management"""
        for slave in placard.models.get_slave_ids():
            if not tldap.transaction.is_managed(using=slave):
                tldap.transaction.enter_transaction_management(using=slave)

    def process_exception(self, request, exception):
        """Rolls back the database and leaves transaction management"""
        for slave in placard.models.get_slave_ids():
            if tldap.transaction.is_dirty(using=slave):
                tldap.transaction.rollback(using=slave)

    def process_response(self, request, response):
        """Commits and leaves transaction management."""
        for slave in placard.models.get_slave_ids():
            if tldap.transaction.is_managed(using=slave):
                if tldap.transaction.is_dirty(using=slave):
                    tldap.transaction.commit(using=slave)
                tldap.transaction.leave_transaction_management(using=slave)
        return response

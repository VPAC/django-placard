from django.contrib.auth.middleware import RemoteUserMiddleware
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.contrib import auth

from placard import LDAPClient


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
        user = auth.authenticate(remote_user=username)
        if not user:
            # Create user
            conn = LDAPClient()
            ldap_user = conn.get_user("uid=%s" % username)
            user = User.objects.create_user(ldap_user.uid, ldap_user.mail)
            try:
                user.first_name = ldap_user.givenName
            except AttributeError:
                pass
            try:
                user.last_name = ldap_user.sn
            except AttributeError:
                pass
            user.save()
    
        # User is valid.  Set request.user and persist user in the session
        # by logging the user in.
        request.user = user
        auth.login(request, user)



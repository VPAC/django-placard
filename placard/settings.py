INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'placard',
    'andsome',
    'andsome.layout',
    'ajax_select',
)


ROOT_URLCONF = 'placard.urls'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'andsome.middleware.threadlocals.ThreadLocals',
    'django.middleware.doc.XViewMiddleware',
    'tldap.middleware.TransactionMiddleware',
)

STATIC_URL = '/media/'

AJAX_LOOKUP_CHANNELS = {
    'account'  : ( 'placard.lookups', 'AccountLookup' ),
    'group'  : ( 'placard.lookups', 'GroupLookup' )
}

AJAX_SELECT_BOOTSTRAP = True
AJAX_SELECT_INLINES = 'staticfiles'

PLACARD_MODELS = 'demo.models'
LDAP_PASSWD_SCHEME = 'ssha'

LOGIN_URL = "/login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_URL = "/logout"

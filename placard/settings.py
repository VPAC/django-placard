INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'placard',
    'ajax_select',
    'django.contrib.admin',
)


ROOT_URLCONF = 'placard.urls'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'tldap.middleware.TransactionMiddleware',
    'placard.middleware.TransactionMiddleware',
)

STATIC_URL = '/media/'

AJAX_LOOKUP_CHANNELS = {
    'account'  : ( 'placard.lookups', 'AccountLookup' ),
    'group'  : ( 'placard.lookups', 'GroupLookup' )
}

AJAX_SELECT_BOOTSTRAP = True
AJAX_SELECT_INLINES = 'staticfiles'

LOGIN_URL = "/login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_URL = "/logout"

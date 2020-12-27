# Configuration-folder/settings/prod_settings.py
# Add security related items in this file such as passwords and keys

# import everything from settings.py i.e. import os etc.
from .settings import *


# Now overwrite necessary items

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
# since DEBUG is False, therefore it is compulsory to add ALLOWED_HOSTS
ALLOWED_HOSTS = ['*'] # add correct hostname i.e. website name


# SECURITY WARNING: keep the secret key used in production secret!
# Create new secret key (just add few more letters in original key)
SECRET_KEY = os.environ.get("secret_key")


# Database : Add production database details here
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# # Email
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True


# #crispy form settings
# CRISPY_TEMPLATE_PACK = 'bootstrap3'


# #django-registration-redux settings
# ACCOUNT_ACTIVATION_DAYS=7
# REGISTRATION_AUTO_LOGIN=True
# SITE_ID=1
# LOGIN_REDIRECT_URL='/'


# SITE_HOST = 'smtp.onlinebookstore.elasticbeanstalk.com'


# # add all sites for calling API
# CORS_ORIGIN_ALLOW_ALL = True
# # #API call for specific sites
# # CORS_ORIGIN_REGEX_WHITELIST = (  ## Test these regexes somewhere - if your API won't allow AJAX calls from a whitelisted site your regexes are probably the problem
# #     r'^https?://(.+\.)?fake.co.nz',
# #     r'^https?://(.+\.)?fake.net.nz',
# # )
# # CORS_ALLOW_METHODS = (
# #     'GET',
# #     'OPTIONS',
# # 
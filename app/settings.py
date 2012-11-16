"""

=======================================================================

Authors:
    Monk )2011)
    Lorenzo (2011-2012)
    Yamashi (2012) >Y<

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
MYSITE_PATH = "/".join(os.path.abspath(__file__).split("/")[0:-1])

# Django settings for mysite project.
from settings_personal import * # pylint: disable=W0614,W0401

#######################################################################

# your username on a Unix machine
USERNAME = 'www'

# if development features should be enabled
DEVELOPMENT = True

# if True, lots of output gets printed onto the console.
# should be false in production.
VERBOSE = DEVELOPMENT

# if True, only a site saying "Down for Maintenance" is accessible
UNDER_MAINTENANCE = False

# Shows a warning on non-english pages that translations are still in progress.
TRANSLATIONS_DONE = False

# true if the server allows outbound connections and can get client IP
# addresses, false otherwise. Requires GeoIP package.
NORMALSERVER = True

# authentication profile
AUTH_PROFILE_MODULE = "user.Profile"

# When false, the whole site is publicly accessible by anybody.
TOKENSACTIVE = False
SPLASHPAGENOTOKENS = True

DOMAIN = PRJ_DOMAIN

# character set and rules for loginphrases and ids
CHARS = "ACDEFHJKLMNPQRTUVWXY"
NUMBERS = "0123456789"
ALPHABET = CHARS + NUMBERS
TYPO_CONVERSION = {
    "B":"8",
    "I":"1",
    "O":"0",
    "S":"5",
    "G":"6",
    "Z":"2",
}
LOGINPHRASE_LENGTH = 16
ID_REGEX = "^[A-Z]{2}[1-9][0-9]{3}$"

# number of local and global contacts
NUM_LOCAL_FRIENDS = 6
NUM_REMOTE_FRIENDS = 6

# dropped signal content
DROPPED_CONTENT = "DROPPED"

# Django security
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
#SESSION_COOKIE_SECURE = True

# None of these CSRF settings actually exist:
#CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_AGE = 86400

# Captcha
CAPTCHA_LENGTH = 5
CAPTCHA_FONT_SIZE = 25

LOGIN_REDIRECT_URL = '/user/profile/'
LOCALE_PATHS = (
   MYSITE_PATH+'/locale'
)

# http or https, for sending links in emails
PROTOCOL = "https"

# password hash salting
SALT_FILE = MYSITE_PATH + "/" + HASH_SALT_FILE

# What the format of the account number should look like.
# the array can be arbitrarily long and it determines
# the length of the char groups
# ex.
# your_number = 012345678901
# ACCNT_FORMAT = [1, 2, 3]
# would lead to:
# 0 12 345 678901
ACCNT_FORMAT = [6]

#######################################################################

DEBUG = DEVELOPMENT
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    (USERNAME, PRJ_ADMIN),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'postgresql', 'mysql',
        # 'sqlite3' or 'oracle'.
        'ENGINE': SQL_ENGINE,
        # Or path to database file if using sqlite3.    
        'NAME': SQL_NAME,
        # Not used with sqlite3.
        'USER': SQL_USER,
        # Not used with sqlite3.
        'PASSWORD': SQL_PASSWD,
        # Set to empty string for localhost. Not used with sqlite3.
        'HOST': SQL_HOST,
        # Set to empty string for default. Not used with sqlite3.
        'PORT': SQL_PORT,
        'OPTIONS': SQL_OPTIONS
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html

LANGUAGE_CODE = 'en'

__ = lambda s: s # dummy function (required)

SPOKEN_LANGUAGES = [
  ('ar', 'Arabic'),
  ('az', 'Azerbaijani'),
  ('bg', 'Bulgarian'),
  ('bn', 'Bengali'),
  ('bs', 'Bosnian'),
  ('ca', 'Catalan'),
  ('cs', 'Czech'),
  ('cy', 'Welsh'),
  ('da', 'Danish'),
  ('de', 'German'),
  ('el', 'Greek'),
  ('en', 'English'),
  ('es', 'Spanish'),
  ('et', 'Estonian'),
  ('eu', 'Basque'),
  ('fa', 'Persian'),
  ('fi', 'Finnish'),
  ('fr', 'French'),
  ('fy-nl', 'Frisian'),
  ('ga', 'Irish'),
  ('gl', 'Galician'),
  ('he', 'Hebrew'),
  ('hi', 'Hindi'),
  ('hr', 'Croatian'),
  ('hu', 'Hungarian'),
  ('id', 'Indonesian'),
  ('is', 'Icelandic'),
  ('it', 'Italian'),
  ('ja', 'Japanese'),
  ('ka', 'Georgian'),
  ('km', 'Khmer'),
  ('kn', 'Kannada'),
  ('ko', 'Korean'),
  ('lt', 'Lithuanian'),
  ('lv', 'Latvian'),
  ('mk', 'Macedonian'),
  ('ml', 'Malayalam'),
  ('mn', 'Mongolian'),
  ('nl', 'Dutch'),
  ('no', 'Norwegian'),
  ('pa', 'Punjabi'),
  ('pl', 'Polish'),
  ('pt', 'Portuguese'),
  ('ro', 'Romanian'),
  ('ru', 'Russian'),
  ('sk', 'Slovak'),
  ('sl', 'Slovenian'),
  ('sq', 'Albanian'),
  ('sr', 'Serbian'),
  ('sr-latn', 'Serbian Latin'),
  ('sv', 'Swedish'),
  ('ta', 'Tamil'),
  ('te', 'Telugu'),
  ('th', 'Thai'),
  ('tr', 'Turkish'),
  ('uk', 'Ukrainian'),
  ('ur', 'Urdu'),
  ('vi', 'Vietnamese'),
  ('zh-cn', 'Simplified Chinese'),
  ('zh-tw', 'Traditional Chinese')
]
# expand this list - use something better than django's languages.
# (Swahili is missing here for example)

TRANSLATED_LANGUAGES = {
  'de': __('German'),
  'en': __('English'),
}

SPLASH_LANGUAGES = {
  'de': __('German'),
  'en': __('English'),
}


SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = MYSITE_PATH+'/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = \
    '809=comuTpeGbBj?wUJq6SQ/$syDh,dr-5K3FHLP2' \
    '#4W}R&1%+JfyBZVuHRk48UStxwMePsrLlq6cm0KiC'


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

# Custom backend using our authentication system without usernames
AUTHENTICATION_BACKENDS = (
   'accounts.backend.GpgBackend',
)

ROOT_URLCONF = 'app.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or
    # "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    MYSITE_PATH+'/templates'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable Django debugging
    # 'django_trace',
    # Uncomment the next line to enable the admin:
    #'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    #'django.contrib.admindocs',
    'user',
    'accounts',
    'content',
    'captcha',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

TEMPLATE_CONTEXT_PROCESSORS = (
   'django.contrib.auth.context_processors.auth',
   'django.core.context_processors.debug',
   'django.core.context_processors.i18n',
   'django.core.context_processors.media',
   'django.core.context_processors.static',
   'django.contrib.messages.context_processors.messages',
   'user.context_processors.settings_vars',
   'content.context_processors.settings_vars',
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
FEEDBACK_EMAIL = PRJ_FEEDBACK

### UBUNTU PACKAGES INSTALLED ###
# python-django
# python-setuptools
# python-mysqldb
# gettext
# (not yet) memcached
# (not anymore) python-geoip geoip-bin geoip-database (required?)

### MANUALLY INSTALLED PACKAGES ###
# django-simple-captcha http://code.google.com/p/django-simple-captcha/ with
#     'sudo easy_install django-simple-captcha'
# for styles: http://twitter.github.com/bootstrap/ custom css generated with
#    less: sudo apt-get install libnode-less
# generate style: "lessc lib/bootstrap.less > bootstrap.css" (use the
#    bootstrap.less file from user/static/css)
#    "lessc --compress lib/bootstrap.less > bootstrap.min.css"

### OTHER INSTALLATION STEPS ###
# mysql commands:
# CREATE USER portal;
# CREATE DATABASE portal;
# GRANT ALL ON portal.* TO portal;
#
# start server:
# python manage.py syncdb
# python manage.py runserver

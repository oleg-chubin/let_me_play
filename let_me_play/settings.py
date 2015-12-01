# -*- coding: utf-8 -*-
"""
Django settings for let_me_play project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_8i5)4a1o6%0$77$$me27mj!6y%577*)(=5%a2!%*3(4p(aebt'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']



# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'autocomplete_light',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',)

if DEBUG:
    INSTALLED_APPS += ('debug_toolbar', 'template_timings_panel')

INSTALLED_APPS += (
    'annoying',
    'sorl.thumbnail',
    'django.contrib.gis',
    'leaflet',

    'let_me_auth',

    'social.apps.django_app.default',

    'let_me_app',
    'let_me_escort',

    'floppyforms',

)

if DEBUG:
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.sql.SQLPanel',
        'template_timings_panel.panels.TemplateTimings.TemplateTimings',
    ]

TEMPLATE_LOADERS = (
    (
        'django.template.loaders.cached.Loader',
        (
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        )
    ),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
    'django.core.context_processors.request',

    'let_me_app.context_processors.user_events',
    'let_me_app.context_processors.oject_statuses',
)

AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.google.GoogleOAuth2',
    'social.backends.twitter.TwitterOAuth',
    'social.backends.vk.VKOAuth2',
    'social.backends.odnoklassniki.OdnoklassnikiOAuth2',
    'social.backends.email.EmailAuth',
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',)

if DEBUG:
    MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',)

MIDDLEWARE_CLASSES += (
    'let_me_auth.middleware.LoginRequiredMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'let_me_play.urls'

WSGI_APPLICATION = 'let_me_play.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGES = [('en', 'English'), ('ru', 'Русский')]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, 'locale'),
)

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    # os.path.join(PROJECT_ROOT, 'assets'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

LOGIN_EXEMPT_NAMESPACES = ('social', 'let_me_auth')
DEFAULT_VIEW_NAME = 'let_me_escort:view_dashboard'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/done/'
SOCIAL_AUTH_STRATEGY = 'social.strategies.django_strategy.DjangoStrategy'
SOCIAL_AUTH_STORAGE = 'social.apps.django_app.default.models.DjangoStorage'
SOCIAL_AUTH_USER_FIELDS = ['email']
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/home/'
SOCIAL_AUTH_LOGIN_URL = '/login/'
# SOCIAL_AUTH_EMAIL_FORM_URL = '/signup-email'
SOCIAL_AUTH_EMAIL_FORM_HTML = 'email_signup.html'
SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = 'let_me_auth.mail.send_validation'
SOCIAL_AUTH_EMAIL_VALIDATION_URL = '/email-sent/'
EMAIL_SECRET_KEY = "some salt as secret"
SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'let_me_auth.pipeline.email_creator',
    'social.pipeline.mail.mail_validation',
    'social.pipeline.social_auth.associate_by_email',
    'social.pipeline.user.create_user',
    'let_me_auth.pipeline.user_password',
#     'let_me_auth.pipeline.get_user_by_email',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    #'social.pipeline.debug.debug'
)

### Social network secure keys
# twitter
#Go to https://apps.twitter.com/app/new and create the new application
#The callback URL should be something like http://test1.com:8000/complete/twitter/
SOCIAL_AUTH_TWITTER_KEY = os.environ.get('SOCIAL_AUTH_TWITTER_KEY')
SOCIAL_AUTH_TWITTER_SECRET = os.environ.get('SOCIAL_AUTH_TWITTER_SECRET')

#google OAuth2
#Go to https://console.developers.google.com/ and create a new application.
#Under APIs and Auth > Credentials, create a new Client ID.
#Make sure to specify the right callback URL: http://test1.com:8000/complete/google-oauth2/
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')

#facebook
#Go to https://developers.facebook.com/apps/?action=create and click the green “Create New App” button.
#In the settings of the newly-created application, click “Add Platform”.
# From the options provided, choose Web,
# and fill in the URL of the site (http://test1.com:8000 in our example).
SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get('SOCIAL_AUTH_FACEBOOK_SECRET')

#VK
#http://psa.matiasaguirre.net/docs/backends/vk.html#oauth2
SOCIAL_AUTH_VK_SCOPE = ['email']  # configure how the data is labelled on SocialAuth.extra_data
SOCIAL_AUTH_VK_EXTRA_DATA = ['email',]
SOCIAL_AUTH_VK_OAUTH2_SCOPE = ['email']
SOCIAL_AUTH_VK_OAUTH2_EXTRA_DATA = ['email',]

SOCIAL_AUTH_VK_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_VK_OAUTH2_KEY')
SOCIAL_AUTH_VK_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_VK_OAUTH2_SECRET')

#OK
SOCIAL_AUTH_ODNOKLASSNIKI_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_ODNOKLASSNIKI_OAUTH2_KEY')
SOCIAL_AUTH_ODNOKLASSNIKI_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_ODNOKLASSNIKI_OAUTH2_SECRET')
SOCIAL_AUTH_ODNOKLASSNIKI_OAUTH2_PUBLIC_NAME = os.environ.get('SOCIAL_AUTH_ODNOKLASSNIKI_OAUTH2_PUBLIC_NAME')

# EmailAuth
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = bool(os.environ.get('EMAIL_USE_TLS', True))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_FROM = os.environ.get('EMAIL_FROM')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Parse database configuration from $DATABASE_URL
DATABASES['default'] = dj_database_url.config()

AUTH_USER_MODEL = 'let_me_auth.User'

LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (6.0, 45.0),
    'DEFAULT_ZOOM': 16,
    'MIN_ZOOM': 3,
    'MAX_ZOOM': 18,
}

try:
    from .local_settings import *
except ImportError:
    pass

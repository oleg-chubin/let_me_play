from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

urlpatterns = patterns('let_me_auth.views',
    url(r'^home/$', 'home'),
    url(r'^done/$', 'done', name='done'),
    url(r'^signup/$', 'signup', name="signup"),
    url(r'^set_password/$', 'set_password', name='initial_password'),
    url(r'^email-sent/', 'validation_sent'),
    url(r'^email/$', 'require_email', name='require_email'),
)

from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from let_me_auth.views import (EditUserView, ProfileDetailsView,
    CreateConfirmationCodeView, CheckConfirmationCodeView, SettingsView)
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('let_me_auth.views',
    url(r'^home/$', 'home'),
    url(r'^done/$', 'done', name='done'),
    url(r'^signup/$', 'signup', name="signup"),
    url(r'^set_password/$', 'set_password', name='initial_password'),
    url(r'^email-sent/', 'validation_sent'),
    url(r'^email/$', 'require_email', name='require_email'),
    url(r'^profile/$', login_required(login_url='/login/')(ProfileDetailsView.as_view()),
        name='profile_details'),
    url(r'^update/profile/$',
        login_required(login_url='/login/')(EditUserView.as_view()),
        name='update_profile'),

    url(r'^confirmationcode/generate/$',
        login_required(login_url='/login/')(CreateConfirmationCodeView.as_view()),
        name='generate_confirmation_code'),
    url(r'^confirmationcode/check/$',
        login_required(login_url='/login/')(CheckConfirmationCodeView.as_view()),
        name='check_confirmation_code'),

    url('my/settings/',
        login_required(SettingsView.as_view()), name="user_settings"),

)

from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

from .views import CreateCourtView

urlpatterns = patterns('',
    url(r'create/court/$', CreateCourtView.as_view()),
)
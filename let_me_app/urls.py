from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

from . import views

urlpatterns = patterns('',
    url(r'create/court/$', views.CreateCourtView.as_view()),
    url(r'create/site/$', views.SiteCreateView.as_view(), name='site-create'),
    url(r'view/site/(?P<pk>[\d]*)/details/$',
        views.SiteDetailView.as_view(), name='site-details'),
    url(r'update/site/(?P<pk>[\d]*)/$',
        views.SiteUpdateView.as_view(), name='site-update'),
    url(r'view/site/list/$',
        views.SiteListView.as_view(), name='site-list'),
)
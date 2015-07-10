'''
Created on Jul 5, 2015

@author: oleg
'''
from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    url(r'^results/$', views.DashboardView.as_view(), name='view_dashboard'),
    url(r'^followable/(?P<pk>[0-9]+)/$', views.EscortFollowable.as_view(), name='escort_followable'),
    url(r'^/stop/for/followable/(?P<pk>[0-9]+)/$',
        views.StopEscortFollowable.as_view(), name='stop_escort_followable'),
)
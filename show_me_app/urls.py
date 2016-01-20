'''
Created on Jul 5, 2015

@author: oleg
'''
from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    url(r'^courts/$', views.CourtListView.as_view(), name='court_list_view'),
    url(r'^court/(?P<pk>[0-9]+)/events/$', views.CourtEventsView.as_view(), name='court_events_view'),
)

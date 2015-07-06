'''
Created on Jul 5, 2015

@author: oleg
'''
from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    url(r'^results/$', views.DashboardView.as_view(), name='view_dashboard'),
)
from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    url(r'^view/event/(?P<pk>[0-9]+)/$',
        views.EventView.as_view(),
        name='view_event'),
    url(r'^cancel/application/for/event/(?P<event>[0-9]+)/$',
        views.CancelApplicationView.as_view(),
        name="cancel_application"),
    url(r'^decline/application/for/event/(?P<event>[0-9]+)/$',
        views.DeclineProposalEventView.as_view(),
        name="decline_proposal"),
    url(r'^accept/application/for/event/(?P<event>[0-9]+)/$',
        views.AcceptProposalView.as_view(),
        name="accept_proposal"),
)
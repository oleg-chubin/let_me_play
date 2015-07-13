from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    url(r'^view/event/(?P<pk>[0-9]+)/$',
        views.EventView.as_view(),
        name='view_event'),
    url(r'^view/my/events/$',
        views.UserEventListView.as_view(),
        name='user_events'),
    url(r'^view/my/proposals/$',
        views.UserProposalsListView.as_view(),
        name='user_proposals'),
    url(r'^view/events/managed/by/me$',
        views.UserManagedEventListView.as_view(),
        name='user_managed_events'),
    url(r'^cancel/event/(?P<event>[0-9]+)/$',
        views.CancelEventView.as_view(),
        name='cancel_event'),
    url(r'^complete/event/(?P<event>[0-9]+)/$',
        views.CompleteEventView.as_view(),
        name='complete_event'),
    url(r'^view/court/(?P<pk>[0-9]+)/$',
        views.CourtDetailView.as_view(),
        name='view_court'),
    url(r'^create/application/for/event/(?P<event>[0-9]+)/$',
        views.CreateApplicationView.as_view(),
        name="create_application"),
    url(r'^cancel/application/for/event/(?P<event>[0-9]+)/$',
        views.CancelApplicationView.as_view(),
        name="cancel_application"),
    url(r'^decline/proposal/for/event/(?P<event>[0-9]+)/$',
        views.DeclineProposalEventView.as_view(),
        name="decline_proposal"),
    url(r'^accept/proposal/for/event/(?P<event>[0-9]+)/$',
        views.AcceptProposalView.as_view(),
        name="accept_proposal"),
    url(r'^decline/application/for/event/(?P<event>[0-9]+)/$',
        views.DeclineApplicationEventView.as_view(),
        name="decline_application"),
    url(r'^accept/user/(?P<user>[0-9]+)/application/for/event/(?P<event>[0-9]+)/$',
        views.AcceptApplicationView.as_view(),
        name="accept_application"),
    url(r'^cancel/visit/for/event/(?P<event>[0-9]+)/$',
        views.CancelVisitView.as_view(),
        name="cancel_visit"),
    url(r'^dismiss/visitor/(?P<user>[0-9]+)/for/event/(?P<event>[0-9]+)/$',
        views.DismissVisitorEventView.as_view(),
        name="dismiss_visit"),

    url(r'^cancel/proposal/(?P<user>[0-9]+)/for/event/(?P<event>[0-9]+)/$',
        views.CancelProposalEventView.as_view(),
        name="cancel_proposal"),
    url(r'^create/proposal/for/event/(?P<event>[0-9]+)/$',
        views.CreateProposalView.as_view(),
        name="create_proposal"),

    url(r'^remove/(?P<user>[0-9]+)/from/admingroup/for/court/(?P<court>[0-9]+)/$',
        views.RemoveFromAdminGroup.as_view(),
        name="remove_from_admin_group"),
    url(r'^add/users/to/admingroup/for/court/(?P<court>[0-9]+)/$',
        views.AddUserToAdminGroupView.as_view(),
        name="add_user_to_admin_group"),


    url(r'^view/chat/list/$', views.ChatList.as_view(), name="chat_list"),
    url(r'^view/chat/(?P<pk>[0-9]+)/$',
        views.ChatDetails.as_view(), name="chat_details"),
    url(r'^post/chat/(?P<pk>[0-9]+)/message/$',
        views.PostChatMessage.as_view(), name="post_chat_message"),
)
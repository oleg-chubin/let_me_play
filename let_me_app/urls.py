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

    url(r'^cancel/event/(?P<event>[0-9]+)/$',
        views.CancelEventView.as_view(),
        name='cancel_event'),
    url(r'^complete/event/(?P<event>[0-9]+)/$',
        views.CompleteEventView.as_view(),
        name='complete_event'),

    url(r'^view/court/(?P<pk>[0-9]+)/$',
        views.CourtDetailView.as_view(),
        name='view_court'),
    url(r'^view/courts/managed/by/me$',
        views.UserManagedCourtsListView.as_view(),
        name='user_managed_courts'),
    url(r'^offer/courts/$',
        views.CourtSearchView.as_view(), name='search_courts'),

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
    url(r'^decline/application/(?P<application>[0-9]+)/for/event/(?P<event>[0-9]+)/$',
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

    url(r'^remove/visitor/role/(?P<role>[0-9]+)/for/event/(?P<event>[0-9]+)/$',
        views.RemoveVisitRoleEventView.as_view(),
        name="remove_role"),
    url(r'^update/visitor/(?P<visit>[0-9]+)/role/for/event/(?P<event>[0-9]+)/$',
        views.UpdateVisitRoleEventView.as_view(),
        name="update_role"),

    url(r'^cancel/inventory/(?P<inventory>[0-9]+)/$',
        views.CancelInventoryEventView.as_view(),
        name="cancel_inventory"),
    url(r'^add/inventory/for/event/(?P<pk>[0-9]+)/$',
        views.AddEventInventoryView.as_view(),
        name="add_event_inventory"),
    url(r'^add/inventory/for/application/(?P<pk>[0-9]+)/$',
        views.AddApplicationInventoryView.as_view(),
        name="add_application_inventory"),
    url(r'^add/inventory/for/visit/(?P<pk>[0-9]+)/$',
        views.AddVisitInventoryView.as_view(),
        name="add_visit_inventory"),

    url(r'^cancel/proposal/(?P<user>[0-9]+)/for/event/(?P<event>[0-9]+)/$',
        views.CancelProposalEventView.as_view(),
        name="cancel_proposal"),
    url(r'^create/proposal/for/event/(?P<pk>[0-9]+)/$',
        views.CreateProposalView.as_view(),
        name="create_proposal"),
    url(r'^create/visit/for/event/(?P<pk>[0-9]+)/$',
        views.CreateVisitView.as_view(),
        name="create_visit"),

    url(r'^remove/(?P<user>[0-9]+)/from/admingroup/for/court/(?P<court>[0-9]+)/$',
        views.RemoveFromAdminGroup.as_view(),
        name="remove_from_admin_group"),
    url(r'^add/users/to/admingroup/for/court/(?P<court>[0-9]+)/$',
        views.AddUserToAdminGroupView.as_view(),
        name="add_user_to_admin_group"),

    url(r'^view/site/(?P<pk>[0-9]+)/$',
        views.SiteDetailView.as_view(),
        name='view_site'),

    url(r'^nominate/staff/for/event/(?P<pk>[0-9]+)/$',
        views.CreateStaffView.as_view(),
        name='nominate_staff'),

    url(r'^create/new/event/$',
        views.CreateEventView.as_view(),
        name='create_new_event'),
    url(r'^create/new/event/for/site/(?P<site>[0-9]+)/$',
        views.CreateSiteEventView.as_view(),
        name='create_site_event'),
    url(r'^create/new/event/for/sites/(?P<site>[0-9]+)/court/(?P<court>[0-9]+)$',
        views.CreateCourtEventView.as_view(),
        name='create_court_event'),

    url(r'^clone/event/(?P<event>[0-9]+)/$',
        views.CloneEventView.as_view(),
        name='clone_event'),

    url(r'^annotate/visit/(?P<visit_id>[0-9]+)/$',
        views.AnnotateVisitView.as_view(),
        name='annotate_visit'),
    url(r'^see/index/charts/(?P<user_id>[0-9]+)/$',
        views.IndexCharts.as_view(),
        name='view_index_charts'),
    url(r'^see/index/recommendations/(?P<user_id>[0-9]+)/$',
        views.IndexRecommendations.as_view(),
        name='view_visit_recommendations'),

    url(r'^offer/events/$',
        views.EventSearchView.as_view(), name='search_events'),

    url(r'^view/chat/list/$', views.ChatList.as_view(), name="chat_list"),
    url(r'^view/chat/(?P<pk>[0-9]+)/$',
        views.ChatDetails.as_view(), name="chat_details"),
    url(r'^post/chat/(?P<pk>[0-9]+)/message/$',
        views.PostChatMessage.as_view(), name="post_chat_message"),
)

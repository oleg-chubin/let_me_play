from django.conf.urls import url
from let_me_app.views.ajax import RateUserView, ManageGroup


urlpatterns = [
    url(
        'rate/user/(?P<user_id>[0-9]+)/$',
        RateUserView.as_view(), name='rate-user',
    ),
    url(
        'update/group/(?P<pk>[0-9]+)/$',
        ManageGroup.as_view(), name='update-group',
    ),
]

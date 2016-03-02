from django.conf.urls import url
from let_me_app.views.ajax import RateUserView


urlpatterns = [
    url(
        'rate/user/(?P<user_id>[0-9]+)/$',
        RateUserView.as_view(), name='rate-user',
    ),
]

from django.conf.urls import include, url
from give_me_app import views


urlpatterns = (
    url(r'^events/$', views.EventList.as_view(), name='events_list'),
)

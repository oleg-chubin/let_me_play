from django.conf.urls import include, url
from let_me_app import views

urlpatterns = (
    url(r'^get/events/$', views.ReactEventList.as_view(), name='new_tableau'),

)

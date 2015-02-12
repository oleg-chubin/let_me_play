from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'let_me_app.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^$', 'let_me_app.views.login'),
    url(r'^home/$', 'let_me_app.views.home'),
    url(r'^done/$', 'let_me_app.views.done', name='done'),
    url(r'^logout/$', 'let_me_app.views.logout'),
    url(r'^signup/$', 'let_me_app.views.signup', name="signup"),
    url(r'^email-sent/', 'let_me_app.views.validation_sent'),
    url(r'^email/$', 'let_me_app.views.require_email', name='require_email'),
)

if settings.DEBUG:
    if settings.MEDIA_ROOT:
        urlpatterns += static(settings.MEDIA_URL,
            document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()


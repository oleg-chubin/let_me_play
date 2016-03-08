from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings


urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'let_me_auth.views.home', name='home'),
    url(r'^', include('django.contrib.auth.urls')),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include('let_me_auth.urls', namespace='let_me_auth')),
    url('^show/me/', include('show_me_app.urls', namespace='show_me_app')),
    url('^let/me/', include('let_me_app.urls.urls', namespace='let_me_app')),
    url('^help/me/', include('let_me_app.urls.ajax_urls', namespace='let_me_help')),
    url('', include('let_me_app.urls.autocomplete_urls')),

    url('^escort/', include('let_me_escort.urls', namespace='let_me_escort')),
#     url('^autocomplete/', include('autocomplete_light.urls')),
#    url(r'^email/$', 'let_me_app.views.require_email', name='require_email'),
    url('/i18n/', include('django.conf.urls.i18n')),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
    if settings.MEDIA_ROOT:
        urlpatterns += static(settings.MEDIA_URL,
            document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()


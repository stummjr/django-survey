import settings
from django.contrib import admin
from django.conf.urls import patterns, include, url
from views import MyRegistrationView


admin.autodiscover()
media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')

urlpatterns = patterns(
    '',
    url(r'^$', 'survey.views.Index', name='home'),
    url(r'^survey/(?P<id>\d+)/$',
        'survey.views.SurveyDetail', name='survey_detail'),
    url(r'^confirm/(?P<uuid>\w+)/$',
        'survey.views.Confirm', name='confirmation'),
    url(r'^privacy/$', 'survey.views.privacy',
        name='privacy_statement'),
    url(r'^admin/doc/', include(
        'django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/register/$', MyRegistrationView.as_view()),
    url(r'^accounts/', include('registration.backends.simple.urls')),
)


# media url hackery. le sigh.
urlpatterns += patterns(
    '',
    (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
)

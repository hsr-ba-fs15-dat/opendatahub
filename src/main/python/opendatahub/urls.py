from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'opendatahub.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'django.views.static.serve', {'path': 'index.html', 'document_root': '../webapp/app'}),
    url(r'^bower_components/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '../webapp/bower_components'}),
    url(r'^styles/main\.css$', 'django.views.static.serve', {'path': '.tmp/styles/main.css', 'document_root': '../webapp'}),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': '../webapp/app'}),
)

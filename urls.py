from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^browser/', include('apps.catalog.urls')),
	(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
	(r'^logout/', 'django.contrib.auth.views.logout', {'template_name': 'login.html'}),
	#(r'^accounts/login/(?P<next_page>.*)/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
	(r'^admin/', include(admin.site.urls)),
	(r'^importer/', include('apps.importer.urls')),
	(r'^retailer/', include('apps.retailer.urls')),	
	(r'^coc/', include('apps.coc.urls')),
	(r'^build/', include('apps.coc.urls')),
		
	(r'^public/$', 'apps.coc.views.home_public'),
	(r'^search_public/$', 'apps.coc.views.search_public'),
)

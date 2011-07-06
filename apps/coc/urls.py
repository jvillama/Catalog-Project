from django.conf.urls.defaults import *

urlpatterns = patterns('',	
	(r'^$', 'apps.coc.views.home'),
	(r'^search/$', 'apps.coc.views.search'),
	#(r'^(\d+)/$', 'apps.coc.views.'),
	#(r'^coc-app/files/(?P<company>[A-Za-z]+)/(?P<filename>.+)/$', 'apps.coc.views.download'),
)

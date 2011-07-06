from django.conf.urls.defaults import *

urlpatterns = patterns('dim-sum.apps.importer.views',
	(r'^sample/$', 'importer'),
	(r'^cat/$', 'importerCategoryS3'),
	(r'^import/$', 'importLines'),
)

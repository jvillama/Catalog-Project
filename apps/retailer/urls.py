from django.conf.urls.defaults import *

urlpatterns = patterns('',	
	(r'^$', 'apps.retailer.views.index'),
	(r'^reset/', 'apps.retailer.views.S3reset'),
	(r'^sync/', 'apps.retailer.views.S3sync'),
	(r'^seasonals/', 'apps.retailer.views.seasonal'),
	(r'^fixtures/', 'apps.retailer.views.fixture'),
	(r'^documents/', 'apps.retailer.views.document'),
	
	#----------HIDDEN RETAILER FUNCTIONS----------
	(r'^uploadFile/', 'apps.retailer.views.uploadFile'),
	
)

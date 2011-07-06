from django.conf.urls.defaults import *
                             
urlpatterns = patterns('apps.catalog.views',
	(r'^$', 'index', {}, "index"),
	(r'^passwordChange$', 'passwordChange'),
	(r'^logout$', 'logoutCatalog'),
	(r'^(?P<line>[A-Za-z_\d\']+)/$', 'line'),
	(r'^(?P<line>[A-Za-z_\d\']+)/(?P<category>\bBags/Purses\b)/$', 'category'),
	(r'^(?P<line>[A-Za-z_\d\']+)/(?P<category>\bL/S_Knits\b)/$', 'category'),
	(r'^(?P<line>[A-Za-z_\d\']+)/(?P<category>[A-Za-z_\d\&\-]+)/$', 'category'),
	(r'^(?P<line>[A-Za-z_\d\']+)/(?P<category>\bBags/Purses\b)/(?P<style>[A-Za-z\d]+)/$', 'style'),
	(r'^(?P<line>[A-Za-z_\d\']+)/(?P<category>\bL/S_Knits\b)/(?P<style>[A-Za-z\d]+)/$', 'style'),
	(r'^(?P<line>[A-Za-z_\d\']+)/(?P<category>[A-Za-z_\d\&\-]+)/(?P<style>[A-Za-z\d]+)/$', 'style'),
	(r'^(?P<line>[A-Za-z_\d\']+)/(?P<category>\bBags/Purses\b)/(?P<style>[A-Za-z\d]+)/(?P<color>[A-Za-z\d]+)/$', 'color'),
	(r'^(?P<line>[A-Za-z_\d\']+)/(?P<category>\bL/S_Knits\b)/(?P<style>[A-Za-z\d]+)/(?P<color>[A-Za-z\d]+)/$', 'color'),
	(r'^(?P<line>[A-Za-z_\d\']+)/(?P<category>[A-Za-z_\d\&\-]+)/(?P<style>[A-Za-z\d]+)/(?P<color>[A-Za-z\d]+)/$', 'color'),
	(r'^clear$', 'clear_cache'),
)

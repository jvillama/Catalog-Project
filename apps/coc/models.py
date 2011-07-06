from django.db import models

class Company(models.Model):
	name = models.TextField(max_length=255)
	description = models.TextField(blank=True)
	ftp_server = models.TextField(blank=True)
	ftp_username = models.TextField(blank=True)
	ftp_password =  models.TextField(blank=True)
	ftp_url = models.TextField(blank=True)
	
	def natural_key(self):
		return (self.name)
		
	def __unicode__(self):
		return u'%s - %s - %s' % (self.name, self.description, self.ftp_url)

class File(models.Model):
	uid = models.CharField(max_length=100)
	company = models.ForeignKey(Company)
	description = models.TextField()
	file_name = models.TextField(max_length=255)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField()
	
	def __unicode__ (self):
		return self.file_name
	
	class Admin:
	        pass
	
class App_Data(models.Model):
	uid = models.IntegerField()
	last_update = models.DateTimeField()
	sync_interval = models.IntegerField()
	
	class Admin:
			pass

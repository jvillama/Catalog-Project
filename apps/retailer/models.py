from django.db import models
from django.conf import settings
from apps.catalog import S3FileField
from datetime import datetime

class SeasonalImagery(models.Model):
    name = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=500, blank=True)
    imageFile = S3FileField.S3EnabledFileField(upload_to='seasonals')
    url = models.URLField(blank=True)
    last_modified = models.DateTimeField(blank=True, null=True)
    
    def save(self):
        if 'seasonals/' in str(self.imageFile):
            self.url = settings.DEFAULT_BUCKET_URL + str(self.imageFile)
        else:
            self.url = settings.DEFAULT_BUCKET_URL + 'seasonals/' + str(self.imageFile)
        self.last_modified = datetime.now()
        models.Model.save(self)
    
    def __unicode__(self):
        return u'%s - %s' % (self.name, self.url)
    
class ClothingFixture(models.Model):
    name = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=500, blank=True)
    imageFile = S3FileField.S3EnabledFileField(upload_to='fixtures')
    url = models.URLField(blank=True)
    last_modified = models.DateTimeField(blank=True, null=True)
    
    def save(self):
        if 'fixtures/' in str(self.imageFile):
            self.url = settings.DEFAULT_BUCKET_URL + str(self.imageFile)
        else:
            self.url = settings.DEFAULT_BUCKET_URL + 'fixtures/' + str(self.imageFile)
        self.last_modified = datetime.now()
        models.Model.save(self)
        
    def __unicode__(self):
        return u'%s - %s' % (self.name, self.url)
    
class S3File(models.Model):
    name = models.CharField(max_length=100, blank=True, default="")
    description = models.CharField(max_length=200, blank=True)
    file = S3FileField.S3EnabledFileField(upload_to='files')
    contact_email = models.EmailField(blank=True)
    contact_name = models.CharField(max_length=100, blank=True)
    url = models.URLField(blank=True)
    last_modified = models.DateTimeField(blank=True, null=True)
    
    def save(self):
        if 'files/' in str(self.file):
            self.url = settings.DEFAULT_BUCKET_URL + str(self.file)
        else:
            self.url = settings.DEFAULT_BUCKET_URL + 'files/' + str(self.file)
        self.last_modified = datetime.now()
        models.Model.save(self)
    
    def __unicode__(self):
        return u'%s - %s' % (self.file, self.url)
    
class Document(models.Model):
	s3file = models.ForeignKey(S3File)
	
	def __unicode__(self):
		return u'%s' % (str(self.s3file))
	
class Supplement(models.Model):
	s3file = models.ForeignKey(S3File)
	
	def __unicode__(self):
		return u'%s' % (str(self.s3file))
	
class CatalogFile(models.Model):
	s3file = models.ForeignKey(S3File)
	
	def __unicode__(self):
		return u'%s' % (str(self.s3file))
	
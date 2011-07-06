

from django.conf import settings
import S3FileField
from datetime import datetime

from apps.retailer.models import *

def get_line_by_name(line_name):
	line_obj = None
	try:
		line_obj = Line.objects.get(name=line_name)
	except:
		return None
	return line_obj

class Division(models.Model):
	division_id = models.PositiveIntegerField(default=0)
	description = models.CharField(max_length=200, blank=True)
	imageFile = S3FileField.S3EnabledFileField(null=True, blank=True, upload_to='divisionImages')
	imageLink = models.URLField(blank=True)
	
	def save(self):
		if self.imageFile is None or str(self.imageFile) == "":
			models.Model.save(self)
		elif 'divisionImages/' in str(self.imageFile):
			self.imageLink = settings.DEFAULT_BUCKET_URL + str(self.imageFile)
			models.Model.save(self)
		else:
			print self.imageFile
			print str(self.imageFile)
			self.imageLink = settings.DEFAULT_BUCKET_URL + 'divisionImages/' + str(self.imageFile)
			models.Model.save(self)
	
	def __unicode__(self):
		return u'%s - %s - %s' % (self.division_id, self.description, self.imageLink)

class Category(models.Model):
	name = models.CharField(max_length=50)
	
	def __unicode__(self):
		return u'%s' % (self.name)
		
class CategoryMapEntry(models.Model):
	code = models.CharField(max_length=50)
	description = models.CharField(max_length=200, null=True, blank=True)
	simple_name = models.CharField(max_length=100, blank=True)

	def __unicode__(self):
		return u'%s - %s - %s' % (self.code, self.description, self.simple_name)

class Line(models.Model):
	VISIBILITY_CHOICES = (
		('public', 'Public'),
		('private', 'Private'),
		('hidden', 'Hidden'),
	)
	name = models.CharField(max_length=50)
	year = models.PositiveIntegerField(max_length=5)
	season = models.CharField(max_length=10)
	imageFile = S3FileField.S3EnabledFileField(null=True, blank=True, upload_to='lineImages')
	imageLink = models.URLField(blank=True)
	division = models.ForeignKey(Division, null=True, blank=True)
	visibility = models.CharField(default='hidden', choices=VISIBILITY_CHOICES, max_length=15)
	categories = models.ManyToManyField(Category, null=True, blank=True)
	supplements = models.ManyToManyField(Supplement, null=True, blank=True)
	catalogFile = models.ForeignKey(CatalogFile, null=True, blank=True)
		
	def is_hidden(self):
		if self.visibility == 'hidden':
			return True
		return False
		
	def is_public(self):
		if self.visibility == 'public':
			return True
		return False
	
	def underscored_name(self):
		return self.name.replace(' ','_')

	def save(self):
		if self.imageFile is None or str(self.imageFile) == "":
			models.Model.save(self)
		elif 'lineImages/' in str(self.imageFile):
			self.imageLink = settings.DEFAULT_BUCKET_URL + str(self.imageFile)
			models.Model.save(self)
		else:
			self.imageLink = settings.DEFAULT_BUCKET_URL + 'lineImages/' + str(self.imageFile)
			models.Model.save(self)
	
	def __unicode__(self):
		return u'%s - %s - %s' % (self.name, self.visibility, self.imageLink)

class Style(models.Model):
	number = models.CharField(max_length=20)
	description = models.CharField(max_length=50, blank=True)
	details = models.CharField(max_length=200, blank=True)
	contentID = models.IntegerField(null=True, blank=True, default=0)
	contentDesc = models.CharField(max_length=200, blank=True)
	avail = models.DateTimeField(null=True, blank=True)
	line = models.ForeignKey(Line, null=True, blank=True)
	category = models.ForeignKey(Category, null=True, blank=True)
	size = models.CharField(max_length=100, default="")
	
	def __unicode__(self):
		return u'%s - %s' % (self.number, self.description)
		
class Product(models.Model):
	colorCode = models.CharField(max_length=10)
	colorDesc = models.CharField(max_length=200, blank=True)
	colorAvail = models.DateTimeField(null=True, blank=True)
	imageFile = S3FileField.S3EnabledFileField(null=True, blank=True, upload_to='productImages')
	imageLink = models.URLField(blank=True)
	style = models.ForeignKey(Style, null=True, blank=True)

	def save(self):
		if self.imageFile is None or str(self.imageFile) == "":
			models.Model.save(self)
		elif 'productImages/' in str(self.imageFile):
			self.imageLink = settings.DEFAULT_BUCKET_URL + str(self.imageFile)
			models.Model.save(self)
		else:
			self.imageLink = settings.DEFAULT_BUCKET_URL + 'productImages/' + str(self.imageFile)
			models.Model.save(self)
	
	def __unicode__(self):
		return u'%s - %s - %s' % (self.style.number, self.colorDesc, self.imageLink)
		
class FeaturedProduct(models.Model):
	product = models.ForeignKey(Product)
	
	def __unicode__(self):
		return u'%s - %s - %s' % (self.product.style.number, self.product.style.description, self.product.colorDesc)
		
class FeaturedLine(models.Model):
	line = models.ForeignKey(Line)

	def __unicode__(self):
		return u'%s' % (self.line.name)
		

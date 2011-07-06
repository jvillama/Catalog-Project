from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import csv
import time
from ftplib import FTP

from datetime import datetime
from apps.catalog.models import *
from apps.retailer.forms import *

from django.conf import settings
from boto.s3.connection import S3Connection
from boto.s3.key import Key

#------------Importer functions----------------------
rownum = 0 # Global rownum

@login_required
def index(request):
    return HttpResponse("Hello world")

def get_cat_map(catID):
	categoryMapEntry = None
	try:
		categoryMapEntry = CategoryMapEntry.objects.get(code = catID)
	except:
		return None
	return categoryMapEntry

def get_season_name(seasonCode):
	seasonName = ""
	try:
		if seasonCode == "SP":
			seasonName = "Spring"
		if seasonCode == "SU":
			seasonName = "Summer"
		if seasonCode == "FA":
			seasonName = "Fall"
		if seasonCode == "WI":
			seasonName = "Winter"
	except:
		print "SeasonCode Error"
	return seasonName
	
def get_s3_csv_list():
	try:
		conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
		b = conn.get_bucket(settings.CATALOG_CSV_BUCKET)
		rs = b.get_all_keys()
		print rs
		
		Division.objects.all().delete() # Clear/Reset db and import from csv files
		global rownum
		
		for key in rs:
			rownum = 0 # Clear global rownum
			#key.getfile()
			print key
			#key.get_contents_to_filename(file)
			file = key.get_contents_as_string()
			#file = StringIO()
			#key.get_file(file)
			if "\r" in file:
				print "got here r"
				file = file.split('\r') # Split data by ASCII Carriage Return (CR) from old school MAC saves
				for row in file:
					print row
					importer(row)
			elif "\n" in file:
				print "got here n"
				file = file.split('\n') # Split data by new line
				for row in file:
					print row
					importer(row)
	except:
		raise
		
def get_ftp_csv_list():
	files = []
	
	ftp = FTP( settings.CATALOG_FTP_SERVER )
	ftp.login( settings.CATALOG_FTP_USERNAME, settings.CATALOG_FTP_PASSWORD, 10 )
	ftp.cwd( settings.CATEGORY_CSV_FILES )
	files = ftp.nlst()
	
	Division.objects.all().delete() # Clear/Reset db and import from csv files
	global rownum
	for file in files:
		if file.find( '.csv' ) >= 0:			
			#csv_list.append( file )
			rownum = 0 # Clear global rownum
			try:
				ftp.retrlines('RETR ' + file, normalize) # Import lines from files to db
			except:
				print "get_ftp_csv_list() error 1"
				print file
				raise
	ftp.quit()
	
def normalize(data):	
	global rownum
	if "\r" in data:
		data = data.split('\r') # Split data by ASCII Carriage Return (CR) from old school MAC saves
		print rownum
		for row in data:
			importer(data[rownum]) # Import line from file to db
	else: # It's a UNIX or Windows save format
		print "File contains ASCII Linefeed (LF) or (CRLF)"
		importer(data) # Import line from file to db
		
def RepresentsInt(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False
	
def importer(row):
	global rownum
	row = row.split(',')
	time_format = "%m/%d/%Y"
	categoryMapEntry = None
	
	if rownum == 0:
		pass
	else:
		try:
			styleNum = 		row[0]
			styleDesc = 	row[1]
			styleDet = 		row[2]
			try:
				contentID = int(row[3])
			except:
				contentID = 0
			contentDesc = 	row[4]
			size = 			row[5]
			colorCode = 	row[6]
			colorDesc = 	row[7]
			styleAvail = 	row[8]
			colorAvail = 	row[9]
			category = 		row[10]
			catDesc = 		row[11]
			divDesc = 		row[12]
			seasonCode = 	row[13].strip()
						
			lineSeason = get_season_name(seasonCode[0:2])
			lineYear = "20" + seasonCode[2:4] # Get season year from last two digits in seasonCode
			lineName = divDesc + " " + lineSeason + " " + lineYear
			category_name = ""
			
			if not styleAvail == '':
				styleAvail = datetime.fromtimestamp(time.mktime(time.strptime(styleAvail, time_format)))
				
			if not colorAvail == '':
				colorAvail = datetime.fromtimestamp(time.mktime(time.strptime(colorAvail, time_format)))
					
			if RepresentsInt(category):
				category_map = get_cat_map(category)
				category_name = category_map.simple_name		
			else:
				category_name = catDesc
		except IndexError as err:
			print row
			print err
		except ValueError as err: # Error from datetime
			print "ValueError: Next row"
			print row
			print err
		except:
			print "Something else errored"
			print row
			raise
		
		currDiv = None
		currLine = None
		currCat = None
		currStyle = None
			
		try:
			currDiv = Division.objects.get(description=divDesc)
		except ObjectDoesNotExist as err:
			currDiv = Division()
			currDiv.description = divDesc
			currDiv.save()
		except:
			print "Something else errored"
			print row
			raise
		
		try:
			currCat = Category.objects.get(name=category_name)
		except AttributeError: # categoryMapEntry is None, Skip
			print categoryMapEntry
		except ObjectDoesNotExist as err:
			currCat = Category(name=category_name)
			currCat.save()
		except:
			print "Something else errored"
			print row
			raise
			
		try:
			currLine = Line.objects.get(name=lineName)
		except ObjectDoesNotExist as err:
			currLine = Line(name=lineName)
			currLine.year = lineYear
			currLine.season = lineSeason
			currLine.division = currDiv
			currLine.save()
		except:
			print "Something else errored"
			print row
			raise
			
		try:
			currLine.categories.get( currCat )
		except ObjectDoesNotExist as err:
			print row
			print err
			if currCat != None:
				currLine.categories.add( currCat )
		except TypeError as err:
			print row
			print err
			if currCat != None:
				currLine.categories.add( currCat )
		except:
			print "Something else errored"
			print row
			raise
			
		try:
			currStyle = Style.objects.get(number=styleNum)
		except:
			currStyle = Style(number=styleNum)
			currStyle.description = styleDesc
			currStyle.details = styleDet
			currStyle.contentID = contentID
			currStyle.contentDesc = contentDesc
			currStyle.avail = styleAvail
			currStyle.line = currLine
			currStyle.category = currCat
			currStyle.save()

		try:
			newProduct = Product()
			newProduct.colorCode = colorCode
			newProduct.colorDesc = colorDesc
			if not colorAvail == '':
				newProduct.colorAvail = colorAvail
			newProduct.style = currStyle
			newProduct.save()
		except:
			print row
			raise
		'''
		print "final"
		print currDiv
		print currLine
		print currCat
		print currStyle
		print newProduct
		'''
	rownum += 1 
	#return HttpResponse("Catalog Import Success")

@login_required
def importerCategoryS3(request):
	def importCat(row):
		global rownum
		if rownum == 0:
			print row
		else:	
			webCategory = None			
			try:
				currCat = CategoryMapEntry()
				codeCat = row.split(',')[0]
				currCat.code = codeCat
				descCat = row.split(',')[1]
				currCat.description = descCat
				webCategory = row.split(',')[2]
				currCat.simple_name = webCategory
				currCat.save()
				print currCat
			except IndexError as err:
				print "IndexError: Next row"
				#print currCat
				#print err
				currCat.save() # Save current status of CategoryMapEntry and move on
				print currCat
			except:
				print "Something else errored"
				print row
				raise
		rownum += 1

	try:
		conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
		b = conn.get_bucket(settings.CATEGORY_MAP_BUCKET)
		rs = b.get_all_keys()
		print rs
		
		CategoryMapEntry.objects.all().delete()
		global rownum
		
		for key in rs:
			rownum = 0 # Clear global rownum
			#key.getfile()
			print key
			#key.get_contents_to_filename(file)
			file = key.get_contents_as_string()
			#file = StringIO()
			#key.get_file(file)
			if "\r" in file:
				file = file.split('\r') # Split data by ASCII Carriage Return (CR) from old school MAC saves
				for row in file:
					importCat(row)
			elif "\n" in file:
				file = file.split('\n') # Split data by new line
				for row in file:
					importCat(row)
	except:
		raise
	return HttpResponse("CategoryMapEntries Uploaded")
	
@login_required
def importerCategory(request):
	files = []
	ftp = FTP( settings.CATALOG_FTP_SERVER )
	ftp.login( settings.CATALOG_FTP_USERNAME, settings.CATALOG_FTP_PASSWORD, 10 )
	
	CategoryMapEntry.objects.all().delete()
	global rownum
	rownum = 0 # Clear global rownum
	
	def importCat(row):
		global rownum
		if "\r" in row:
			row = row.split('\r') # Split data by ASCII Carriage Return (CR) from old school MAC saves
			print rownum
			for r in row:
				print r
				importCat(r[rownum]) # Loop and import line from file to db
		row = row.split(',')
		#print row	
		if rownum == 0:
			print row
		else:			
			webCategory = None			
			try:
				currCat = CategoryMapEntry()
				codeCat = row[0]
				currCat.code = codeCat
				descCat = row[1]
				currCat.description = descCat
				webCategory = row[2]
				currCat.simple_name = webCategory
				currCat.save()
			except IndexError as err:
				print "IndexError: Next row"
				print currCat
				#print err
				currCat.save() # Save current status of CategoryMapEntry and move on
			except:
				print "Something else errored"
				print row
				raise
		rownum += 1
		
	ftp.retrlines('RETR ' + settings.CATEGORY_MASTER_MAP, importCat)
	ftp.quit()

	return HttpResponse("CategoryMapEntries Uploaded")
	
@login_required
def importLines(request): # Skeleton of manual line import
	try:
		#get_ftp_csv_list()
		get_s3_csv_list()
		return HttpResponse(".csv files from ftp folder uploaded")
	except:
		print "get_ftp_csv_list() list empty or another error!"
		raise
	
	return HttpResponse("importLines() error!")
	
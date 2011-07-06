from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render_to_response
from django.conf.urls.defaults import *
from models import *
from ftplib import FTP
from datetime import datetime
from django.utils import simplejson as json
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.template import Template, context, RequestContext

import urllib

from django.conf import settings
from boto.s3.connection import S3Connection
from boto.s3.key import Key

def get_ftp_filelist( company ): # deprecated, getting list from S3
	files = []
	
	#try:
	ftp = FTP( company.ftp_server )
	ftp.login( company.ftp_username , company.ftp_password, 10 ) 
	ftp.cwd( company.ftp_url )
	files = ftp.nlst()
	ftp.quit()
	
	pdf_list = []
	
	for f in files:
		if f.find( '.pdf' ) >= 0:
			pdf_list.append( f )
	
	return pdf_list
	
def download(request, company, filename): # not used, may be used if ftp is implemented again
	company = Company.objects.get(name=company)
	ftp = FTP( company.ftp_server )
	ftp.login( company.ftp_username , company.ftp_password, 10 ) 
	ftp.cwd( company.ftp_url )
	
	file = open(filename, 'wb')
	ftp.retrbinary('RETR '+ filename, file.write)
	response = HttpResponse(open(filename, 'rb'), mimetype='application/pdf')
	# If you want to download as attachment, uncomment next line
	#response['Content-Disposition'] = 'attachment; filename='+filename
	
	return response

def get_files_by_string( query, companies ):
	files_by_id = {}
	files_by_description = {}
	final_search_set = []
	found_companies = []
	
	for c in companies:
		try:
			found_companies.append( Company.objects.get( name__iexact=c ) )
		except:
			found_companies.append( Company.objects.get( name__iexact=c.name ) )
			print "Can't find query or query error"
			print found_companies
			print c
	try:
		files_by_description = File.objects.filter( description__icontains=query )
	except:
		pass

	try:
		files_by_id = File.objects.filter( uid__icontains=query )
	except:
		pass
		
	for f_by_id in files_by_id:
		final_search_set.append( f_by_id )

	id_found = False
	for f_by_descrip in files_by_description:
		for f_by_id in files_by_id:
			if f_by_descrip.uid == f_by_id.uid:
				id_found = True
		if not id_found:
			final_search_set.append( f_by_descrip )
		id_found = False
		
	company_found = False
	index = 0
	for f in final_search_set[:]:
		for c in found_companies:
			if f.company == c:
				company_found = True
		if not company_found:
			final_search_set.remove( f )
		company_found = False
		index = index + 1
		
	return final_search_set
	
@login_required
def home(request):

	app_data = []
	debug = {}
	sync_latest = False
	current_time = datetime.now()
	last_sync_time = 0
	time_delta = 0
	
	query = request.GET.get('q')
	companies = request.GET.getlist('company')
	app_date = None
	
	#check to see if we should sync
	try:
		app_data = App_Data.objects.get( uid=0 )
	except Exception, e:
		app_data = App_Data( uid=0, last_update=datetime.now(), sync_interval=1200 )
		app_data.save()
		sync_latest = True
		
	time_delta = current_time - app_data.last_update 
	
	if time_delta.seconds > app_data.sync_interval:
		sync_latest = True
		app_data.last_update=datetime.now()
		app_data.save()
		
		
	companies = Company.objects.all()
	print companies
	
	if sync_latest:
		File.objects.all().delete()
		print "syncing"
		
		for company in companies:
			print company
			#file_list = get_ftp_filelist( company ) #deprecated
			#print file_list

			try:
				conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
				b = conn.get_bucket(settings.COC_BUCKET)
				#rs = b.get_all_keys()
				rs = b.list(company.name)
				print rs
				for key in rs:
					#print key.name
					file_chunks = key.name.split('.')
					new_file =  File( uid=file_chunks[0].split('/')[1],
								description=file_chunks[1], 
								modified=datetime.now(), 
								file_name=key.name.split('/')[1], 
								company=company )
					new_file.save()
			except:
				raise
			''' deprecated as well
			for f in file_list:
				file_chunks = f.split('.')
				new_file =  File( uid=file_chunks[0], 
								description=file_chunks[1], 
								modified=datetime.now(), 
								file_name=f, 
								company=company )
				new_file.save()
			'''				
	if query:
		files = get_files_by_string(query, companies)
	else:
		query = ""
		files = File.objects.all()[:200]	
		
	return render_to_response('coc.html', { 'files': files, 'query': query, 'companies': companies, 'user': request.user}, context_instance=RequestContext(request) )
	
@login_required
def search(request):
	q = request.GET.get('q')	
	companies = request.GET.getlist('company')
	
	filtered_files = get_files_by_string( q, companies )
		
	json_data = serializers.serialize( "json", filtered_files )
	return HttpResponse(json_data, mimetype='application/json')	

def home_public(request):

	app_data = []
	debug = {}
	sync_latest = False
	current_time = datetime.now()
	last_sync_time = 0
	time_delta = 0
	
	query = request.GET.get('q')
	companies = request.GET.getlist('company')
	app_date = None
	
	#check to see if we should sync
	try:
		app_data = App_Data.objects.get( uid=0 )
	except Exception, e:
		app_data = App_Data( uid=0, last_update=datetime.now(), sync_interval=1200 )
		app_data.save()
		sync_latest = True
		
	time_delta = current_time - app_data.last_update 
	
	if time_delta.seconds > app_data.sync_interval:
		sync_latest = True
		app_data.last_update=datetime.now()
		app_data.save()
		
		
	companies = Company.objects.all()
	print companies
	
	if sync_latest:
		File.objects.all().delete()
		print "syncing"
		
		for company in companies:
			print company
			#file_list = get_ftp_filelist( company ) #deprecated
			#print file_list

			try:
				conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
				b = conn.get_bucket(settings.COC_BUCKET)
				#rs = b.get_all_keys()
				rs = b.list(company.name)
				print rs
				for key in rs:
					#print key.name
					file_chunks = key.name.split('.')
					new_file =  File( uid=file_chunks[0].split('/')[1],
								description=file_chunks[1], 
								modified=datetime.now(), 
								file_name=key.name.split('/')[1], 
								company=company )
					new_file.save()
			except:
				raise
	
	if query:
		files = get_files_by_string(query, companies)
	else:
		query = ""
		files = File.objects.all()[:200]	
		
	return render_to_response('coc_public.html', { 'files': files, 'query': query, 'companies': companies, 'user': request.user}, context_instance=RequestContext(request) )
	
def search_public(request):
	q = request.GET.get('q')	
	companies = request.GET.getlist('company')
	
	filtered_files = get_files_by_string( q, companies )
		
	json_data = serializers.serialize( "json", filtered_files )
	return HttpResponse(json_data, mimetype='application/json')	

	
#def server_error(request):
#	return render_to_response('500.html')
	
	

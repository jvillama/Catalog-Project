from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404
from models import *
from forms import *
from django.contrib.auth.decorators import login_required
from django.template import Template, context, RequestContext

# s3 stuff
import mimetypes
from django.conf import settings
from boto.s3.connection import S3Connection
from boto.s3.key import Key

from django.core.exceptions import ObjectDoesNotExist

@login_required
def index(request):
	#return render_to_response('retailer.html', {'user': request.user})
	return HttpResponseRedirect('/catalog/browser')

@login_required
def S3reset(request):
	S3File.objects.all().delete()
	SeasonalImagery.objects.all().delete()
	ClothingFixture.objects.all().delete()
	S3sync(request)
	return HttpResponse("S3Files Reset/Resynced")
	
@login_required
def S3sync(request):
	try:
		conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
		b = conn.get_bucket(settings.DEFAULT_BUCKET)
		print "syncing S3Files..."
		#rs = b.get_all_keys()
		rs = b.list('files')
		#print rs
		for key in rs:
			#print key
			try:
				currS3File = S3File.objects.get(file=key.name)
				#print currS3File
			except ObjectDoesNotExist as err:
				new_file =  S3File(
								name=key.name.split('/')[1],
								file=key.name,
								#url=settings.DEFAULT_BUCKET_URL+key.name
								)
				print new_file
				new_file.save()
			except:
				print "Something errored in S3Files part of retailer/views.py"
				print S3File.objects.all()
				raise
		print "syncing seasonals..."
		rs = b.list('seasonals')
		for key in rs:
			try:
				currSeasonal = SeasonalImagery.objects.get(imageFile=key.name)
				#print currSeasonal
			except ObjectDoesNotExist as err:
				new_file =  SeasonalImagery(
								name=key.name.split('/')[1],
								imageFile=key.name,
								)
				print new_file
				new_file.save()
			except:
				print "Something errored in seasonals part of retailer/views.py"
				print SeasonalImagery.objects.all()
				raise
		print "syncing fixtures..."
		rs = b.list('fixtures')
		for key in rs:
			try:
				currFixture = ClothingFixture.objects.get(imageFile=key.name)
				#print currFixture
			except ObjectDoesNotExist as err:
				new_file =  ClothingFixture(
								name=key.name.split('/')[1],
								imageFile=key.name,
								)
				print new_file
				new_file.save()
			except:
				print "Something errored in fixtures part of retailer/views.py"
				print ClothingFixture.objects.all()
				raise
	except:
		print "Something else errored in retailer/views.py"
		raise
	#return render_to_response('retailer.html', {'user': request.user}, context_instance=RequestContext(request))
	return HttpResponse("S3Files Synced/Refreshed")
	
@login_required
def seasonal(request):
	seasonals = SeasonalImagery.objects.all().order_by("-last_modified")
	return render_to_response('seasonal.html', {"seasonals":seasonals, "user":request.user}, context_instance=RequestContext(request))

@login_required
def fixture(request):
	fixtures = ClothingFixture.objects.all().order_by("-last_modified")
	return render_to_response('fixture.html', {"fixtures":fixtures, "user":request.user}, context_instance=RequestContext(request))

@login_required
def document(request):
	documents = Document.objects.all()
	return render_to_response('document.html', {"docs":documents, "user":request.user}, context_instance=RequestContext(request))
	
@login_required
def supplement(request):
	sups = Supplement.objects.all()
	return render_to_response('supplement.html', {"sups":sups, "user":request.user}, context_instance=RequestContext(request))
	
#---------------HIDDEN RETAILER FUNCTIONS-------------------
	
@login_required
def store_in_s3(filename, content):
	conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
	if not conn.lookup(settings.DEFAULT_BUCKET):
		b = conn.create_bucket(settings.DEFAULT_BUCKET)
			#b = conn.get_bucket(settings.DEFAULT_BUCKET)
	mime = mimetypes.guess_type(filename)[0]
	k = Key(b)
	k.key = filename
	k.set_metadata("Content-Type", mime)
	k.set_contents_from_file(content)
	k.set_acl("public-read")
	
@login_required
def uploadFile(request):
	user = request.user
	files = S3File.objects.all().order_by("-last_modified")
	if not request.method == "POST":
		f = UploadFileForm()
		return render_to_response("retailer.html", {"form":f, "files":files, "user":user}, context_instance=RequestContext(request))

	f = UploadFileForm(request.POST, request.FILES)
	if not f.is_valid():
		return render_to_response("retailer.html", {"form":f, "files":files, "user":user}, context_instance=RequestContext(request))

	File = request.FILES["file"]
	filename = File.name
	#content = File.content_type
	content = File.file
	print content
	store_in_s3(filename, content)
	fileUrl = S3File(name=filename, url=settings.DEFAULT_BUCKET_URL + filename)
	fileUrl.save()
	
	files = S3File.objects.all().order_by("-last_modified")
	return render_to_response("retailer.html", {"form":f, "files":files, "user":user}, context_instance=RequestContext(request))
	
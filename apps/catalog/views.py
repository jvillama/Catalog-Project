from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.template import Template, context, RequestContext
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
#Let's see DB query
from django.db import connection

from django.middleware.gzip import GZipMiddleware
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from datetime import datetime
from time import strftime

from urllib import unquote

from apps.catalog.models import *

def can_view_line(line_obj, user):
	if line_obj.visibility == 'hidden' and not user.is_authenticated():
		return False
		
	if line_obj.visibility == 'private' and not user.is_authenticated():
		return False
	else:
		return True
		
	if line_obj.visibility == 'public':
		return True
	return False
	
def get_breadcrumbs(request):
	url_chunks = request.path.split('/')
	url_chunks = filter(None, url_chunks)

	#JB: Hack
	try:
		url_chunks.remove('catalog')
	except:
		pass

	breadcrumbs = []

	try:
		snowballed_url = settings.HOME_PATH
	except NameError:
		# using production settings
		snowballed_url = "/catalog/"

	for chunk in url_chunks:
		if chunk == 'Bags':
			breadcrumbs.append( {'name': 'Bags/Purses', 'url': snowballed_url + 'Bags/Purses'} )
			snowballed_url += 'Bags/Purses' + "/"
		elif chunk == 'Purses':
			print 'passing Purses'
		elif chunk == 'L':
			breadcrumbs.append( {'name': 'L/S_Knits', 'url': snowballed_url + 'L/S_Knits'} )
			snowballed_url += 'L/S_Knits' + "/"
		elif chunk == 'S_Knits':
			print 'passing S_Knits'	
		else:
			breadcrumbs.append( {'name': chunk, 'url': snowballed_url + chunk} )
			snowballed_url += chunk + "/"
	return breadcrumbs

def index(request):
	cached_view = cache.get( request.user.username+'_home_web', 'empty' )
	if cached_view != 'empty':
		return cached_view

	breadcrumbs = get_breadcrumbs(request)
	divisions = Division.objects.all()
	featured_lines = FeaturedLine.objects.all()
	
	#return render_to_response('catalog-browser/home.html', 
	response = render_to_response('catalog-browser/home.html', 
		{
		'home_path' : settings.HOME_PATH,
		'breadcrumbs': breadcrumbs, 
		'divisions': divisions,
		'aws_s3_domain': settings.AWS_S3_DOMAIN,
		'featured_lines': featured_lines,
		'user': request.user,
		},
		context_instance=RequestContext(request)
		)
	view = GZipMiddleware().process_response(request, response)
	cache.set( str(request.user)+'_home_web', view )
	return view
		
def test(request, blah):
	return render_to_response('catalog-browser/test.html', {})

def passwordChange(request):
	'''
	send_mail('Password Change Requested', request.user.username + ' is requesting for a new password.', request.user.email,
		fail_silently=False)
	'''
	return render_to_response('password_change_done.html',  {'user': request.user})
	
def logoutCatalog(request):
	logout(request)
	breadcrumbs = get_breadcrumbs(request)
	divisions = Division.objects.all()
	return HttpResponseRedirect('/catalog/browser')
		
def line(request, line):
	cache_key = request.user.username+'_'+line+'_web'
	cached_view = cache.get( cache_key, 'empty' )
	if cached_view != 'empty':
		return cached_view
	
	breadcrumbs = get_breadcrumbs(request)
	line_rep = line.replace('_', ' ')
	line_obj = get_line_by_name( line_rep )
	featured_products = FeaturedProduct.objects.all()

	styles = []
	for featured_product in featured_products:
		if featured_product.product.style.line == line_obj:
			styles.append( featured_product.product )
	
	if not can_view_line(line_obj, request.user):
		return render_to_response('login.html')
		
	#return render_to_response('catalog-browser/line.html', {
	response = render_to_response('catalog-browser/line.html', {
		'home_path' : settings.HOME_PATH,
		'breadcrumbs': breadcrumbs, 
		'line': line_obj, 
		'user': request.user,
		'aws_s3_domain': settings.AWS_S3_DOMAIN,
		'styles': styles,
		},
		context_instance=RequestContext(request)
		)
	view = GZipMiddleware().process_response(request, response)
	cache.set( cache_key, view )
	return view
		
def styledir(line, category, styles): # Creates catalog directory which validates image links and stores previous and next page style numbers
	cached_view = cache.get( line+'_'+category+'_styledir_web', 'empty' )
	if cached_view != 'empty':
		return cached_view
	
	styleslinks = {}	
	validate = URLValidator(verify_exists=True)
	for idx, style in enumerate(styles):
		previdpage = None
		nextidpage = None
		if len(styles)>1:
			if idx == 0:
				previdpage = styles[len(styles)-1]
				nextidpage = styles[idx + 1]
			elif idx > 0 and idx < len(styles)-1:
				previdpage = styles[idx - 1]
				nextidpage = styles[idx + 1]
			else: # Last page
				previdpage = styles[idx - 1]
				nextidpage = styles[0]

		try:
			#link = 'http://images-user-opensocial.googleusercontent.com/gadgets/proxy?url='+settings.AWS_S3_DOMAIN+'/'+style.number+'_'+style.product_set.all()[0].colorCode.upper()+'_F.jpg&container=pos&rewriteMime=image/*&resize_h=234&resize_w=240&no_expand=1&refresh=2592000'
			link = settings.AWS_S3_DOMAIN+'/'+style.number+'_'+style.product_set.all()[0].colorCode.upper()+'_F.jpg'
			validate(link)			
			styleslinks[style] = [link, previdpage, nextidpage]
			
			#styleslinks[style] = link
		except ValidationError, e:
			#print e
			styleslinks[style] = ['http://s3-ap-southeast-1.amazonaws.com/vlcm-catalog-aus/imagenotavailable.jpg', previdpage, nextidpage]
			#styleslinks[style] = [settings.DEFAULT_BUCKET_URL+'imagenotavailable.jpg', previdpage, nextidpage]
			
			#styleslinks[style] = 'http://s3-ap-southeast-1.amazonaws.com/vlcm-catalog-aus/imagenotavailable.jpg'
			#styleslinks[style.number] = settings.DEFAULT_BUCKET_URL+'imagenotavailable.jpg'
		#print idx
		#print style
		#print previdpage
		#print nextidpage
	#print styleslinks
	
	#print connection.queries
	cache.set( line+'_'+category+'_styledir_web', styleslinks )
	return styleslinks

def category(request, line, category):
	breadcrumbs = get_breadcrumbs(request)
	line_rep = line.replace('_', ' ')
	category_rep = category.replace('_', ' ')
	line_obj = get_line_by_name( line_rep )

	category_obj = Category.objects.get(name=category_rep)
	styles = line_obj.style_set.filter(category=category_obj)
	#styleslinks = styledir(styles)
	
	cache_key = request.user.username+'_'+line+'_'+category+'_web'
	cached_view = cache.get( cache_key, 'empty' )
	if cached_view != 'empty':
		return cached_view
	
	if not can_view_line(line_obj, request.user):
		return render_to_response('login.html')
	
	#print connection.queries
	#return render_to_response('catalog-browser/line.html', {
	response = render_to_response('catalog-browser/line.html', {
		'home_path' : settings.HOME_PATH,
		'breadcrumbs': breadcrumbs, 
		'line': line_obj, 
		'selected_category': category_rep, 
		'user': request.user,
		'aws_s3_domain': settings.AWS_S3_DOMAIN,
		'styles': styles,
		},
		context_instance=RequestContext(request)
		)
	view = GZipMiddleware().process_response(request, response)
	cache.set( cache_key, view )
	return view
		
def style(request, line, category, style):
	breadcrumbs = get_breadcrumbs(request)
	line_rep = line.replace('_', ' ')
	category_rep = category.replace('_', ' ')
	line_obj = get_line_by_name( line_rep )	
	style_obj = line_obj.style_set.get(number=style)
	color_obj = style_obj.product_set.all()[0]
	
	cache_key = request.user.username+'_'+line+'_'+category+'_'+style+'_web'
	cached_view = cache.get( cache_key, 'empty' )
	if cached_view != 'empty':
		return cached_view
	
	category_obj = Category.objects.get(name=category_rep)
	styles = line_obj.style_set.filter(category=category_obj)
	
	previdpage = None
	nextidpage = None
	styleslinks = styledir(line, category, styles)
	if not styleslinks[style_obj][1] == None:
		previdpage = styleslinks[style_obj][1].number
	if not styleslinks[style_obj][2] == None:
		nextidpage = styleslinks[style_obj][2].number
	
	if not can_view_line(line_obj, request.user):
		return render_to_response('login.html')
	
	#print connection.queries
	#return render_to_response('catalog-browser/style.html', {
	response = render_to_response('catalog-browser/style.html', {
		'home_path' : settings.HOME_PATH,
		'breadcrumbs': breadcrumbs, 
		'line': line_obj, 
		'selected_category': category_rep, 
		'style': style_obj, 
		'product': color_obj,
		'user': request.user,
		'aws_s3_domain': settings.AWS_S3_DOMAIN,
		'previdpage': previdpage,
		'nextidpage': nextidpage,
		},
		context_instance=RequestContext(request)
		)
	view = GZipMiddleware().process_response(request, response)
	cache.set( cache_key, view )
	return view
	
def color(request, line, category, style, color):
	breadcrumbs = get_breadcrumbs(request)
	line_rep = line.replace('_', ' ')
	category_rep = category.replace('_', ' ')
	line_obj = get_line_by_name( line_rep )
	style_obj = line_obj.style_set.get(number=style)
	color_obj = style_obj.product_set.get(colorCode=color)
	
	cache_key = request.user.username+'_'+line+'_'+category+'_'+style+'_'+color+'_web'
	cached_view = cache.get( cache_key, 'empty' )
	if cached_view != 'empty':
		return cached_view
	
	category_obj = Category.objects.get(name=category_rep)
	styles = line_obj.style_set.filter(category=category_obj)
	
	previdpage = None
	nextidpage = None
	styleslinks = styledir(line, category, styles)
	if not styleslinks[style_obj][1] == None:
		previdpage = styleslinks[style_obj][1].number
	if not styleslinks[style_obj][2] == None:
		nextidpage = styleslinks[style_obj][2].number
	
	if not can_view_line(line_obj, request.user):
		return render_to_response('login.html')
	
	#print connection.queries
	#return render_to_response('catalog-browser/style.html', {
	response = render_to_response('catalog-browser/style.html', { 
		'home_path' : settings.HOME_PATH,
		'breadcrumbs': breadcrumbs, 
		'line': line_obj, 
		'selected_category': category_rep, 
		'style': style_obj,
		'product': color_obj,
		'aws_s3_domain': settings.AWS_S3_DOMAIN,
		'user': request.user,
		'previdpage': previdpage,
		'nextidpage': nextidpage,
		},
		context_instance=RequestContext(request)
		)
	view = GZipMiddleware().process_response(request, response)
	cache.set( cache_key, view )
	return view
	
@login_required	
def clear_cache(request):
	cache.clear()
	#now = datetime.datetime.now()
	now = datetime.time( datetime.now() )
	return HttpResponse("Cache cleared - " + strftime("%H:%M:%S") )
	

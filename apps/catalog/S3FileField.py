# ########################################################
# S3FileField.py
# Extended FileField and ImageField for use with Django and Boto.
#
# Required settings:
#	USE_AMAZON_S3 - Boolean, self explanatory
#	DEFAULT_BUCKET - String, represents the default bucket name to use if one isn't provided
#	AWS_ACCESS_KEY_ID - String
#	AWS_SECRET_ACCESS_KEY - String
#
# ########################################################

from django.db import models
from django.conf import settings
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from django.core.files.storage import FileSystemStorage
from django.core.files import File
import os

class S3Storage(FileSystemStorage):
    def __init__(self, bucket=None, location=None, base_url=None):
        assert bucket
        if location is None:
            location = settings.MEDIA_ROOT
        if base_url is None:
            base_url = settings.MEDIA_URL
        self.location = os.path.abspath(location)
        self.bucket = bucket
        self.base_url = base_url

    def _open(self, name, mode='rb'):
        print name
        class S3File(File):
            def __init__(self, key):
                self.key = key
            
            def size(self):
                return self.key.size
            
            def read(self, *args, **kwargs):
                return self.key.read(*args, **kwargs)
            
            def write(self, content):
                self.key.set_contents_from_string(content)
            
            def close(self):
                self.key.close()
                
        return S3File(Key(self.bucket, name))

    def _save(self, name, content):
        print name
        print content
        name = name.replace('\\', '/')
        key = Key(self.bucket, name)
        print key
        if hasattr(content, 'temporary_file_path'):
            print content.temporary_file_path()
            #mime = mimetypes.guess_type(content.temporary_file_path())[0]
            #print mime
            
            #key.key = filename
            #key.set_metadata("Content-Type", mime)
            
            #key.set_contents_from_filename(content.temporary_file_path())
        elif isinstance(content, File):
            print "key.set_contents_from_file(content)"
            key.set_contents_from_file(content)
            key.set_acl("public-read")
        else:
            print "key.set_contents_from_string(content)"
            #key.set_contents_from_string(content)
        #key.set_acl("public-read")

        return name

    def delete(self, name):
        self.bucket.delete_key(name)

    def exists(self, name):
        return Key(self.bucket, name).exists()

    def listdir(self, path):
        return [key.name for key in self.bucket.list()]

    def path(self, name):
        raise NotImplementedError

    def size(self, name):
        return self.bucket.get_key(name).size

    def url(self, name):
        return Key(self.bucket, name).generate_url(100000)
    
    def get_available_name(self, name):
        return name
        

class S3EnabledFileField(models.FileField):
    def __init__(self, bucket=settings.DEFAULT_BUCKET, verbose_name=None, name=None, upload_to='', storage=None, **kwargs):
        if settings.USE_AMAZON_S3:
            self.connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            if not self.connection.lookup(bucket):
                self.connection.create_bucket(bucket)
            self.bucket = self.connection.get_bucket(bucket)
            storage = S3Storage(self.bucket)
        super(S3EnabledFileField, self).__init__(verbose_name, name, upload_to, storage, **kwargs)    

        
class S3EnabledImageField(models.ImageField):
    def __init__(self, bucket=settings.DEFAULT_BUCKET, verbose_name=None, name=None, width_field=None, height_field=None, **kwargs):
        if settings.USE_AMAZON_S3:
            self.connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            if not self.connection.lookup(bucket):
                self.connection.create_bucket(bucket)
            self.bucket = self.connection.get_bucket(bucket)
            kwargs['storage'] = S3Storage(self.bucket)
        super(S3EnabledImageField, self).__init__(verbose_name, name, width_field, height_field, **kwargs) 
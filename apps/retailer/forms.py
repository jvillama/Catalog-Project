from django import forms
#from django import newforms as forms

class UploadFileForm(forms.Form):
	#title = forms.CharField(max_length=50)
	file  = forms.FileField(label='Select File to upload')
	
class UploadImageForm(forms.Form):
	file = forms.ImageField(label='Select Image to upload')
	
from django.conf import settings # import the settings file


def aws_s3_domain(context):
		# return the value you want as a dictionnary. you may add multiple values in there.
		return {'AWS_S3_DOMAIN': settings.AWS_S3_DOMAIN}
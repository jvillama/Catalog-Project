from apps.retailer.models import *
from django.contrib import admin

class S3FileAdmin(admin.ModelAdmin):
    exclude = ('url',)

admin.site.register(SeasonalImagery, S3FileAdmin)
admin.site.register(ClothingFixture, S3FileAdmin)
admin.site.register(S3File, S3FileAdmin)

admin.site.register(Document)
admin.site.register(Supplement)
admin.site.register(CatalogFile)

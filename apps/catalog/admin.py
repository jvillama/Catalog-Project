from apps.catalog.models import *
from django.contrib import admin

admin.site.register(Division)
admin.site.register(Line)
admin.site.register(Category)
admin.site.register(Style)
admin.site.register(Product)
admin.site.register(FeaturedProduct)
admin.site.register(FeaturedLine)

admin.site.register(CategoryMapEntry)

from django.contrib import admin
from .models import *
admin.site.register(Book)
# admin.site.register(Review)
admin.site.register(Type)
admin.site.register(Cart)
admin.site.register(Author)
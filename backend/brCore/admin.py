from django.contrib import admin
from .models import WatchList, BGTask

# Register your models here.
admin.site.register(WatchList)
admin.site.register(BGTask)

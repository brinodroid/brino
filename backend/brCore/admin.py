from django.contrib import admin
from .models import WatchList, BGTask, PortFolio, ScanEntry

# Register your models here.
admin.site.register(WatchList)
admin.site.register(BGTask)
admin.site.register(PortFolio)
admin.site.register(ScanEntry)

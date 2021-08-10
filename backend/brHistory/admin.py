from django.contrib import admin
from brHistory.models import CallOptionData, PutOptionData, StockData

# Register your models here.
admin.site.register(CallOptionData)
admin.site.register(PutOptionData)
admin.site.register(StockData)

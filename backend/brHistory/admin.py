from django.contrib import admin
from .models import CallOptionData, PutOptionData

# Register your models here.
admin.site.register(CallOptionData)
admin.site.register(PutOptionData)

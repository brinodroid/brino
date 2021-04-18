from django.contrib import admin
from .models import OpenOrder, ExecutedOrder, CancelledOrder

# Register your models here.
admin.site.register(OpenOrder)
admin.site.register(ExecutedOrder)
admin.site.register(CancelledOrder)

from django.urls import include, path
from .views import configuration_rest

urlpatterns = [
    path('config/', configuration_rest)
]


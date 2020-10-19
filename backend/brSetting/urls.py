from django.urls import include, path
from .views import get_configuration

urlpatterns = [
    path('config/', get_configuration)
]


from django.urls import path
from .views import user_data_from_token

urlpatterns = [
    # Return the user data from token
    path('user/', user_data_from_token)
]

from django.urls import include, path
from .views import watchlist_list, watchlist_detail

urlpatterns = [
    path('watchlist/', watchlist_list),
    path('watchlist/<int:pk>', watchlist_detail)
]
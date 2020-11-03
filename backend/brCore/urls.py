from django.urls import include, path
from .views import watchlist_list, watchlist_detail, bgtask_list, bgtask_detail, portfolio_list, portfolio_detail

urlpatterns = [
    path('watchlist/', watchlist_list),
    path('watchlist/<int:pk>', watchlist_detail),
    path('bgtask/', bgtask_list),
    path('bgtask/<int:pk>', bgtask_detail),
    path('portfolio/', portfolio_list),
    path('portfolio/<int:pk>', portfolio_detail),
]

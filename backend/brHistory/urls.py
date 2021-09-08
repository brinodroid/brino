
from django.urls import include, path
from .views import callhistory_list, puthistory_list, stockhistory_list

urlpatterns = [
    path('call/<int:watchlist_id>', callhistory_list),
    path('put/<int:watchlist_id>', puthistory_list),
    path('stock/<int:watchlist_id>', stockhistory_list),
]
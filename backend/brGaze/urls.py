from django.urls import include, path
from .views import update_closest_monthly_options, update_closest_monthly_options_for_all_stocks, train_lstm, infer_lstm

urlpatterns = [
    path('nn/lstm/train/<int:watchlist_id>', train_lstm),
    path('nn/lstm/infer/<int:watchlist_id>', infer_lstm),
    path('inputUpdate/<int:watchlist_id>', update_closest_monthly_options),
    path('inputUpdateAll', update_closest_monthly_options_for_all_stocks)
]
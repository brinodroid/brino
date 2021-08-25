from django.urls import include, path
from brStrategy.views import strategy_list, strategy_detail

urlpatterns = [
    path('strategy/', strategy_list),
    path('strategy/<int:pk>', strategy_detail),
]

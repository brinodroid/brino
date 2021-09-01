from django.urls import include, path
from .views import open_order_list, open_order_detail, \
    executed_order_list, executed_order_detail, \
    cancelled_order_list, cancelled_order_detail, create_order_strategy

urlpatterns = [
    path('order-strategy/', create_order_strategy),
    path('open/', open_order_list),
    path('open/<int:pk>', open_order_detail),
    path('executed/', executed_order_list),
    path('executed/<int:pk>', executed_order_detail),
    path('cancelled/', cancelled_order_list),
    path('cancelled/<int:pk>', cancelled_order_detail),
]
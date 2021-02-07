from django.urls import include, path
from .views import order_list, order_detail

urlpatterns = [
    path('order/', order_list),
    path('order/<int:pk>', order_detail),
]
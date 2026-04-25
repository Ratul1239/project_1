from django.urls import path
from orders.views import place_order,order_complete,custom_dashboard
urlpatterns = [
    path('place_order/',place_order,name='place_order'),
    path('order_complete/',order_complete, name='order_complete'),
    path('my-dashboard/', custom_dashboard, name='custom_dashboard'),

]

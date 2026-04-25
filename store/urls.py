from django.urls import path
from store.views import home,product_detail,search,add_product

urlpatterns = [
    path('', home, name='home'),
    path('<slug:category_slug>/<slug:product_slug>/', product_detail, name='product_detail'),
    path('category/<slug:category_slug>/',home, name='products_by_category'),
    
    path('<slug:category_slug>/<slug:product_slug>/',product_detail, name='product_detail'),
    path('search/', search, name='search'),
    path('add-product/',add_product, name='add_product'), # নতুন লিংক

]
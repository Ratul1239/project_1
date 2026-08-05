from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('carts/', include('carts.urls')),
    path('orders/', include('orders.urls')), 
    path('', include('store.urls')),          
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # for picture show

# ডিবাগ টুলবার কাজ করার জন্য এই অংশটুকু যুক্ত করতে হবে
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
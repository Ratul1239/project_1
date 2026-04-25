from django.contrib import admin
from store.models import Product,Category,VariationManager,Variation,ProductGallery
from orders.models import Order,OrderProduct

admin.site.register(Category)
admin.site.register(Variation)
admin.site.register(Order)
admin.site.register(OrderProduct)

# ১. গ্যালারির জন্য ইনলাইন তৈরি
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

# ২. ProductAdmin এর ভেতরে ইনলাইনটি যুক্ত করে দিন
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline] # এই লাইনটি যোগ করুন

# আগে থেকে যা যা রেজিস্টার করা ছিল...
admin.site.register(Product, ProductAdmin)
# ... বাকিগুলো যেমন ছিল তেমনই থাকবে
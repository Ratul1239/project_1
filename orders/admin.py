from django.contrib import admin
from .models import OrderProduct


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "order",
        "product",
        "quantity",
    ]
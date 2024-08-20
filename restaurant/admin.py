from django.contrib import admin

# Register your models here.
from .models import MenuItem, Booking, Order, OrderItem, Categories, Comments


admin.site.register(MenuItem)
admin.site.register(Booking)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Categories)
admin.site.register(Comments)
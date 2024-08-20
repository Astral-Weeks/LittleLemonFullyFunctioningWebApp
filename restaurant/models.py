from django.db import models
from django.contrib.auth.models import User
# from django_currentuser.middleware import CurrentUserMiddleware
# from django_currentuser.models.fields import CurrentUserField
from django_currentuser.db.models import CurrentUserField
from datetime import datetime
from django.utils import timezone


class Categories(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    description = models.CharField(max_length=500, db_index=True, default="No description")
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Categories, on_delete=models.PROTECT)

    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta():
        unique_together = ('menuitem', 'user')
    def __str__(self):
        return self.user


def current_time():
    return datetime.now().time()

def currenttime():
    return datetime.time(datetime.now())


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="delivery_crew", null=True)
    timeoforder = models.TimeField(default=currenttime)
    status = models.BooleanField(db_index=True, default=0)
    item_updated_at = models.TimeField(default=currenttime)
    delivery_status = models.CharField(max_length=255, db_index=True, default="Your order has been received. You will receive an update when our chefs begin preparing your items.")
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(db_index=True)
    address_line_1 = models.CharField(max_length=255, db_index=True)
    address_line_2 = models.CharField(max_length=255, db_index=True)
    address_town = models.CharField(max_length=255, db_index=True)

    def _str__(self):
        string = f"{self.user.username}"
        return string



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta():
        unique_together = ('order', 'menuitem')

    def _str__(self):
        return self.menuitem, self.order
  


class Booking(models.Model):
    user = CurrentUserField()
    first_name = models.CharField(max_length=200)
    reservation_date = models.DateField()
    reservation_slot = models.SmallIntegerField(default=10)

    def __str__(self): 
        x = "slot number: " + str(self.reservation_slot)
        return self.first_name, self.reservation_date, x, self.user


class Comments(models.Model):
    name = models.CharField(max_length=255)
    comment = models.CharField(max_length=1000)

    def __str__(self):
        return self.name
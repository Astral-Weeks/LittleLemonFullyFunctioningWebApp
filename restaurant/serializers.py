from rest_framework import serializers
from django.contrib.auth.models import User
from .models import MenuItem, Categories, Cart, Order, OrderItem

class UserSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['id', 'username', 'email', 'password']

class ManagerListSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['username']

class CategorySerializer(serializers.ModelSerializer):
    class Meta():
        model = Categories
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta():
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']

class CartSerializer(serializers.ModelSerializer):
    class Meta():
        model = Cart
        fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price']

class AddItemToCartSerializer(serializers.ModelSerializer):
    class Meta():
        model = Cart
        fields = ['menuitem','quantity']
        extra_kwargs = {
            'quantity': {'min_value': 1},
        }
class RemoveFromCartSerializer(serializers.ModelSerializer):
    class Meta():
        model = Cart
        fields = ['menuitem']

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta():
        model = Order
        fields = ['id', 'user', 'total', 'status', 'delivery_crew', 'date']

class ChosenItemSerializer(serializers.ModelSerializer):
    class Meta():
        model = MenuItem
        fields = ['title', 'price']
        
class IndividualOrderSerializer(serializers.ModelSerializer):
    menuitem = ChosenItemSerializer()
    class Meta():
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']


class PatchOrderSerializer(serializers.ModelSerializer):
    class Meta():
        model = Order
        fields = ['delivery_crew']
# from django.http import HttpResponse
from .forms import BookingForm, CommentForm, SignUpForm
from django.core import serializers
from datetime import datetime, date
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from django.views import View
from .permissions import IsManager, IsDeliveryPersonnel
from .models import MenuItem, Booking, Categories, Cart, Order, OrderItem, Comments
from rest_framework import generics, viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .serializers import MenuItemSerializer, CategorySerializer, ManagerListSerializer, CartSerializer, AddItemToCartSerializer, RemoveFromCartSerializer, IndividualOrderSerializer, OrderSerializer, PatchOrderSerializer, UserSerializer
from .paginations import MenuItemPagination
import jwt, datetime
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.views.generic import TemplateView, CreateView, FormView
from rest_framework.decorators import api_view
from django_currentuser.db.models import CurrentUserField


# Create your views here.
def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

class reservations(TemplateView):
    authentication_classes = [IsAuthenticated]
    template_name = 'bookings.html'

        #  cart = Cart.objects.filter(user=self.request.user)
        #     context = {'personalcart': cart}
        #     menu_data = MenuItem.objects.all()
        #     cat_data = Categories.objects.all()
        #     m_data = {"cate": cat_data}
        #     main_data = {"menu": menu_data}
        #     return render(request, 'cart.html', {'personalcart': context, "menu": main_data, "cate": m_data)

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            # date = request.GET.get('date',datetime.date.today())
            bookingstobeshown = Booking.objects.filter(user=self.request.user)
            b = {'bookings': bookingstobeshown}
            # booking_json = serializers.serialize('json', bookings)
            return render(request, 'bookings.html', {'bookings': b})
        else:
            messages.error(request, 'Please login first to see any reservations you have made')
            return redirect('login-page')



def book(request):
    context = {}
    context['form'] = BookingForm()
    if request.user is None:
        return redirect('book')
    else:
        if request.method == 'POST':
            currentuser = request.user
            l = User.objects.get(id=currentuser.id)
            a = Booking(user=l)
            f = BookingForm(request.POST, instance=a)
            if f.is_valid():
                f.save(commit=False)
                f.user = request.user
                f.save()
                messages.success(request, 'Thank you. Your comment has been sent successfully')
            else:
                messages.error(request, 'Something went wrong. Please try again.')

        return render(request, "book.html", context)


# class book(TemplateView):
#     permission_classes = [IsAuthenticated]
#     template_name = 'book.html'
#     form = BookingForm()

# #     def post(self, request, *args, **kwargs):
# #         if self.request.user.is_authenticated:
# #             if request.method == 'POST':
# #                 context = {}
# #                 context['form'] = BookingForm()
# #                 a = Booking()
# #                 form = BookingForm(request.POST, instance=a)
# #                 if form.is_valid():
# #                     form.save(commit=False)
# #                     form.user = request.user
# #                     form.save()
# #                     context = {'form': form}
# #             return render(request, 'book.html', context)
# #         else:
# #             messages.error(request, 'Please login first to see your cart.')
# #             return redirect('book')

#     def post(self, request, *args, **kwargs):
#         if self.request.user.is_authenticated:
#             # x = Booking.objects.get_or_create(user=self.request.user)
#             if request.method == 'POST':
#                 # form = BookingForm(data=self.request.POST, commit=False)
#                 # x = Booking.objects.get_or_create(user=self.request.user, first_name=form.first_name, )
#                 data = self.request.POST
#                 # x.first_name = 
#                 # form.user = self.request.user
#                 # thebooking, created = Booking.objects.get_or_create(user=2, first_name=data.first_name, reservation_date=data.reservation_date, reservation_slot=data.reservation_slot, commit=False)
#                 # thebooking.save()
#                 # thebooking.first_name = "Lucy"
#                 # thebooking.save()
#                 # context = {'thebooking': thebooking}
#             return redirect('book')
#         else:
#             messages.error(request, 'Please login first to see your cart.')
#             return redirect('book')


# class register(FormView):
#     form_class = SignUpForm
#     template_name = "register.html"
#     success_url = 'login-page'
#     success_message = "You have signed up!"

#     def form_valid(self, form):
#             response = super().form_valid(form)
#             success_message = self.get_success_message(form.cleaned_data)
#             if success_message:
#                 messages.success(self.request, success_message)
#             return response

#     def get_success_message(self, cleaned_data):
#         return self.success_message % cleaned_data



class register(FormView):
    form_class = SignUpForm
    template_name = "register.html"
    success_url = 'login-page'

    def form_valid(self, form):
        form.save()
        messages.add_message(self.request, messages.INFO, 'You have signed up successfully!')
        return super().form_valid(form)

def checkusername(request):
    username = request.POST.get('username')
    if get_user_model().objects.filter(username=username):
        return HttpResponse("<div style='color: red;'>This username already exists</div>")
    else:
        return HttpResponse("<div style='color: green;'>This username is available</div>")

# def register2(request):
#     username = request.POST.get('username')
#     if get_user_model().objects.filter(username=username).exists():
#         return HttpResponse('<div style="color: red"> This username already exists</div>')
#     else:
#         return HttpResponse('<div style="color: green"> This username is available</div>')

def signup(request):
    signupcontext = {}
    signupcontext['form'] = SignUpForm()
    if request.method == 'POST':
        suform = SignUpForm(request.POST)
        if suform.is_valid():
            username = suform.cleaned_data.get('username')
            email = suform.cleaned_data.get('email')
            raw_password = suform.cleaned_data.get('password')
            suform.save()
            messages.success(request, 'You have successfully signed up!')
        else:
            messages.error(request, 'Something went wrong. Please try again.')
        signupcontext = {'suform': suform}
    return render(request, 'signup.html', signupcontext)
    

def menu(request):
    menu_data = MenuItem.objects.all()
    cat_data = Categories.objects.all()
    m_data = {"cate": cat_data}
    main_data = {"menu": menu_data}
    return render(request, 'menu.html', {"menu": main_data, "cate": m_data})


def display_menu_item(request, pk=None): 
    if pk: 
        menu_item = MenuItem.objects.get(pk=pk) 
    else: 
        menu_item = "" 
    return render(request, 'menu_item.html', {"menu_item": menu_item}) 

@csrf_exempt
def bookings(request):
    if request.method == 'POST':

        # puts the posted info from the form into JSON
        data = json.load(request)

        # checks if the booking time is unavailable or not
        # returns a boolean value
        exist = Booking.objects.filter(reservation_date=data['reservation_date']).filter(
            reservation_slot=data['reservation_slot']).exists()

        if exist==False:
            booking = Booking(
                first_name=data['first_name'],
                reservation_date=data['reservation_date'],
                reservation_slot=data['reservation_slot'],
            )
            booking.save()
        else:
            return HttpResponse("{'error':1}", content_type='application/json')
    
    date = request.GET.get('date',datetime.date.today())

    bookings = Booking.objects.all().filter(reservation_date=date)
    booking_json = serializers.serialize('json', bookings)

    return HttpResponse(booking_json, content_type='application/json')


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.success(request, ("There was an error."))
            return redirect('login-page')
    else:
        return render(request, 'login.html', {})
    
def logout_user(request):
    logout(request)
    messages.success(request, ("You are logged out"))
    return redirect('home')


# class-based

# class UsersView(generics.ListCreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [IsManager]
#     throttle_classes = [AnonRateThrottle, UserRateThrottle]



# class UsersView(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

#     def get_permissions(self):
#         if self.request.method != 'POST':
#             permission_classes = [IsManager]
#         else:
#             permission_classes = []
#         return [permission() for permission in permission_classes]
    


# CATEGORIES ///////////////////////////////////////////////////////////////

class CategoriesView(generics.ListCreateAPIView):
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    main_data = {"categories": queryset}

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = []
        else:
            permission_classes = [IsManager | IsAdminUser]
        return [permission() for permission in permission_classes]


class ViewByCategoryView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = []
        else:
            permission_classes = [IsManager | IsAdminUser]
        return [permission() for permission in permission_classes]



# MENU ITEMS ///////////////////////////////////////////////////////////////

# class MenuItemsView(generics.ListCreateAPIView):
#     queryset = MenuItem.objects.all()
#     throttle_classes = [AnonRateThrottle, UserRateThrottle]
#     search_fields = ['title', 'category__title']
#     ordering_fields = ['price', 'category']
#     serializer_class = MenuItemSerializer
#     pagination_class = MenuItemPagination

#     def get_permissions(self):
#         if self.request.method == 'GET':
#             permission_classes = []
#         else:
#             permission_classes = [IsManager]
#         return [permission() for permission in permission_classes]


# class IndividualMenuItemView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer
#     throttle_classes = [AnonRateThrottle, UserRateThrottle]

#     def get_permissions(self):
#         if self.request.method == 'GET':
#             permission_classes = []
#         else:
#             permission_classes = [IsManager]
#         return [permission() for permission in permission_classes]



# CART ///////////////////////////////////////////////////////////////

class CartView(TemplateView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    template_name = 'cart.html'
    
    def get_queryset(self, **kwargs):
        cart = Cart.objects.filter(user=self.request.user)
        return cart
    
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            cart = Cart.objects.filter(user=self.request.user)
            context = {'personalcart': cart}
            menu_data = MenuItem.objects.all()
            cat_data = Categories.objects.all()
            m_data = {"cate": cat_data}
            main_data = {"menu": menu_data}
            total_price = 0
            for item in cart:
                total_price += item.price
            try:
                order_data = Order.objects.filter(user=request.user)
                for item in order_data:
                    orderitems = OrderItem.objects.filter(order=item)
                oi_data = {"orderitems": orderitems}
                main_data = {"order": order_data}
                return render(request, 'cart.html', {'personalcart': context, "menu": main_data, "cate": m_data, "total_price": total_price, "order": main_data, "orderitems": oi_data})
            except:
                return render(request, 'cart.html', {'personalcart': context, "menu": main_data, "cate": m_data, "total_price": total_price})
        else:
            messages.error(request, 'Please login first to see your cart.')
            return redirect('login-page')
        
    # @api_view(['POST'])
    def post(self, request, **kwargs):
        serialized_item = AddItemToCartSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        item_from_menu = request.data['menuitem']
        quantity = int(request.data['quantity'])
        item = get_object_or_404(MenuItem, id=item_from_menu)
        total_price = quantity * item.price
        try:
            Cart.objects.create(user=request.user, quantity=quantity, unit_price=item.price, price=total_price, menuitem_id=item_from_menu)
        except:
            return JsonResponse(status=409, data={'Update':'This item has already been added to your cart.'})
        return JsonResponse(status=201, data={'Update':'Success! Your item has been added to your cart. Please add more items, or if you have finished, please submit your order.'})
    
    def delete(self, request, **kwargs):
        if request.data['menuitem']:
            serialized_item = RemoveFromCartSerializer(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            menuitem = request.data['menuitem']
            customer_cart = get_object_or_404(Cart, user=request.user, menuitem=menuitem )
            customer_cart.delete()
            return JsonResponse(status=200, data={'Update':'Your item has been removed from your cart. If this was a mistake, please add it again.'})
        else:
            Cart.objects.filter(user=request.user).delete()
            return JsonResponse(status=201, data={'Update':'All Items removed from cart'})



def add_to_cart(request, id):
    product = MenuItem.objects.get(id=id)
    # product.save()
    item, created = Cart.objects.get_or_create(menuitem=product, user=request.user)
    item.quantity += 1
    item.unit_price = product.price
    item.price = item.quantity * product.price
    item.save()
    return redirect('cart')

def remove_from_cart(request, id):
    cart_item = Cart.objects.get(id=id)
    cart_item.delete()
    return redirect('cart')

# USERS ///////////////////////////////////////////////////////////////

# class UsersView(generics.ListCreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [IsManager]
#     throttle_classes = [AnonRateThrottle, UserRateThrottle]


# DELIVERY PERSONNEL ///////////////////////////////////////////////////////////////
# Delivery personnel can be added or deleted via the admin portal or by the following POST and DELETE HTTP calls
class AllDeliveryPersonnelView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='DeliveryPersonnel')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    # Please use the staff member's username, not their id number, to make the request
    def post(self, request):
        newdeliverymember = request.data['username']
        try:
            user = get_object_or_404(User, username=newdeliverymember)
            deliverypersonnel = Group.objects.get(name='Managers')
            deliverypersonnel.user_set.add(user)
        except:
            return JsonResponse(status=400, data={'Error': 'Bad Request. Please review the information you supplied to see if it is correct, or in the correct format'})
        return JsonResponse(status=201, data={'Update': newdeliverymember + ' has been successfully added to Delivery Personnel'}) 

    # Please use the staff member's username, not their id number, to make the request
    def delete(self, request):
        deliverymembertoremove = request.data['username']
        try:
            user = get_object_or_404(User, username=deliverymembertoremove)
            deliverypersonnel = Group.objects.get(name='Managers')
            deliverypersonnel.user_set.remove(user)
        except:
            return JsonResponse(status=400, data={'Error': 'Bad Request. Please review the information you supplied to see if it is correct, or in the correct format'})
        return JsonResponse(status=201, data={'Update': deliverymembertoremove + ' has been removed from Delivery Personnel'}) 


# MANAGERS ///////////////////////////////////////////////////////////////
# Managers can be added or deleted via the admin portal or by the following POST and DELETE HTTP calls
class AllManagersView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Managers')
    serializer_class = ManagerListSerializer
    permission_classes = [IsManager | IsAdminUser]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    # Please use the staff member's username, not their id number, to make the request
    def post(self, request):
        newmanager = request.data['username']
        try:
            user = get_object_or_404(User, username=newmanager)
            managers = Group.objects.get(name='Managers')
            managers.user_set.add(user)
        except:
            return JsonResponse(status=400, data={'Error': 'Bad Request. Please review the information you supplied to see if it is correct, or in the correct format'})
        return JsonResponse(status=201, data={'Update': newmanager + ' has been successfully added to Managers'}) 

    # Please use the staff member's username, not their id number, to make the request
    def delete(self, request):
        managertoremove = request.data['username']
        try:
            user = get_object_or_404(User, username=managertoremove)
            managers = Group.objects.get(name='Managers')
            managers.user_set.remove(user)
        except:
            return JsonResponse(status=400, data={'Error': 'Bad Request. Please review the information you supplied to see if it is correct, or in the correct format'})
        return JsonResponse(status=201, data={'Update': managertoremove + ' has been removed from Managers'}) 



# ORDERS ///////////////////////////////////////////////////////////////

# class OrderView(generics.ListCreateAPIView):
#     serializer_class = OrderSerializer
#     throttle_classes = [AnonRateThrottle, UserRateThrottle]

#     def get_queryset(self):
#         if self.request.user.groups.filter(name='DeliveryPersonnel').exists():
#             queryset = Order.objects.filter(delivery_crew=self.request.user)
#         elif self.request.user.groups.filter(name='Managers').exists():
#             queryset = Order.objects.all()
#         else:
#             queryset = Order.objects.filter(user=self.request.user)
#         return queryset

#     def get_permissions(self):
#         if self.request.method == 'GET': 
#             permission_classes = [IsAuthenticated]
#         elif self.request.method == 'POST':
#             permission_classes = [IsAuthenticated]
#         else:
#             permission_classes = [IsManager | IsAdminUser]
#         return [permission() for permission in permission_classes]

#     def post(self, request, **kwargs):
#         cart = Cart.objects.filter(user=request.user)
#         allitemsincart = cart.values_list()
#         if len(allitemsincart) == 0:
#             return JsonResponse(status=400, data={'Error': 'Bad Request. There appear to be no items in your cart. Please ensure the cart has items before placing an order'})
#         elif len(allitemsincart) > 0:
#             total = float(0)
#             for i in allitemsincart:
#                 individ_itemprice = float(i[-1])
#                 total += individ_itemprice
#             order = Order.objects.create(user=request.user, status=False, total=total, date=date.today())
#             order_id = str(order.id)
#             for i in cart.values():
#                 menuitem = get_object_or_404(MenuItem, id=i['menuitem_id'])
#                 orderitem = OrderItem.objects.create(order=order, menuitem=menuitem, quantity=i['quantity'], unit_price=i['unit_price'], price=i['price'])
#                 orderitem.save()
#                 data = OrderSerializer(orderitem, many=True).data
#                 Cart.objects.filter(user=request.user).delete()
#                 return JsonResponse(data, safe=False)
                # return redirect('home')
                # return render(request, 'order')
                # return JsonResponse(status=201, data={'Update':'Your order has been received successfully. Your order number is #' + order_id})

# class OrderView(TemplateView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]
#     throttle_classes = [AnonRateThrottle, UserRateThrottle]
#     template_name = 'cart.html'
    
#     def get(self, request, *args, **kwargs):
#         if self.request.user.is_authenticated:
#             if Order.objects.filter(user=request.user).exists():
#                 order_data = Order.objects.filter(user=request.user)
#                 for item in order_data:
#                     orderitems = OrderItem.objects.filter(order=item)
#                     oi_data = {"orderitems": orderitems}
#                     main_data = {"order": order_data}
#                     return render(request, 'order.html', {"item": item, "order": main_data, "orderitems": oi_data})
#             else:
#                 if Cart.objects.filter(user=request.user).exists() is False:
#                     return render(request, 'order.html')
#                 else:
#                     messages.info(request, "You haven't submitted any orders yet. Please add to your cart and submit an order first.")
#                     return redirect('cart')
#         else:
#             messages.error(request, "Please login first to see any orders that you have placed.")
#             return redirect('login-page')
        
#     def post(request):
#         if request.method == 'POST':
#             cart = Cart.objects.filter(user=request.user)
#             if cart.exists():
#                 manager1 = User.objects.get(id=1)
#                 context = {'personalcart': cart}
#                 date = datetime.datetime.today()
#                 total_price = 0
#                 for obj in cart:
#                     total_price += obj.price
#                 order = Order.objects.create(user=obj.user, delivery_crew=manager1, status=False, total=total_price, date=date)
#                 order.save()
#                 for item in cart:
#                     i = OrderItem.objects.create(order=order, menuitem=item.menuitem, quantity=item.quantity, unit_price=item.unit_price, price=item.price)
#                     i.save()
#         # product.save()
#                 Cart.objects.filter(user=request.user).delete()
#                 order_data = Order.objects.filter(user=request.user)
#                 for item in order_data:
#                     orderitems = OrderItem.objects.filter(order=item)
#                 oi_data = {"orderitems": orderitems}
#                 main_data = {"order": order_data}
#                 return render(request, 'order.html', {'personalcart': context, "item": item, "i": i, "total_price": total_price, "order": main_data, "orderitems": oi_data})
#             else:
#                 order_data = Order.objects.filter(user=request.user)
#                 for item in order_data:
#                     orderitems = OrderItem.objects.filter(order=item)
#                 oi_data = {"orderitems": orderitems}
#                 main_data = {"order": order_data}
#                 return render(request, 'order.html', {"order": main_data, "orderitems": oi_data})
#         # return render(request, 'order.html')


# class OrderView(TemplateView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]
#     throttle_classes = [AnonRateThrottle, UserRateThrottle]
#     template_name = 'order.html'

#     def get(self, request, *args, **kwargs):
#         if self.request.user is None:
#             return redirect('login')




def add_to_order(request):
    try:
        cart = Cart.objects.filter(user=request.user)
        if cart.exists():
            manager1 = User.objects.get(id=1)
            context = {'personalcart': cart}
            date = datetime.datetime.today()
            total_price = 0
            for obj in cart:
                total_price += obj.price
            address_line_1 = request.POST.get('address_line_1')
            address_line_2 = request.POST.get('address_line_2')
            address_town = request.POST.get('address_town')

            # delivery_crew can be assigned manually in the admin portal, according to which staff might be
            # closest to the restaurant, as opposed to being without a current delivery

            order = Order.objects.create(user=obj.user, delivery_crew=manager1, status=False, total=total_price, date=date, address_line_1=address_line_1, address_line_2=address_line_2, address_town=address_town)
            order.save()
            for item in cart:
                i = OrderItem.objects.create(order=order, menuitem=item.menuitem, quantity=item.quantity, unit_price=item.unit_price, price=item.price)
                i.save()
        # product.save()
            Cart.objects.filter(user=request.user).delete()
            order_data = Order.objects.filter(user=request.user)
            for item in order_data:
                orderitems = OrderItem.objects.filter(order=item)
            oi_data = {"orderitems": orderitems}
            main_data = {"order": order_data}
            messages.success(request, "Your order has been sent!")
            return render(request, 'order.html', {'personalcart': context, "item": item, "i": i, "total_price": total_price, "order": main_data, "orderitems": oi_data})
        else:
            order_data = Order.objects.filter(user=request.user)
            for item in order_data:
                orderitems = OrderItem.objects.filter(order=item)
            oi_data = {"orderitems": orderitems}
            main_data = {"order": order_data}
            return render(request, 'order.html', {"order": main_data, "orderitems": oi_data})
    except:
        messages.info(request, "You don't currently have any orders pending, nor any items in your cart.")
        messages.info(request, "Feel free to add items to your cart, and place an order when you are ready.")
        messages.info(request, "With care, your LittleLemon team.")
        return redirect('cart')


def addressfordelivery(request):
    return render(request, 'addressfordelivery.html')


def is_member(user):
    return user.groups.filter(name='DeliveryPersonnel').exists()

class stafflogin(TemplateView):
    permission_classes = [IsManager, IsDeliveryPersonnel]
    template_name = "stafflogin.html"
    queryset = Order.objects.all()

    def get(self, request):
        if is_member(self.request.user) is True:
            try:
                assigned_orders = Order.objects.filter(delivery_crew=request.user)
                # if len(assigned_orders) > 0:
                dict = {'assigned_orders': assigned_orders}
                # order_data = Order.objects.filter(user=request.user)
                # for item in assigned_orders:
                orderitems = OrderItem.objects.all()
                oi_data = {"orderitems": orderitems}
                # main_data = {"order": order_data}
                return render(request, 'stafflogin.html', {'assigned_orders': dict, "orderitems": oi_data})
            except:
                messages.info(request, "If you are staff, you need to sign in first.")
                return redirect('login-page')
        else:
            messages.info(request, "You are unauthorized. Only staff can login to the staff page.")
            return redirect('login-page')
    # else:
    #     messages.info(request, "Only staff can login to the staff page. You are not authorized.")
    #     return redirect('login-page')
        
    # def post(request):
    #     try:
    #         x = request.POST.get('thisorder')
    #         print(x)
    #         j, created = Order.objects.get_or_create(id=x.id)
    #         j.address_line_1 = "ewfbkjhbfwhjbfhjwe"
    #         j.save()
    #         return render(request, 'stafflogin.html', {'j': j})
    #     except:
    #         return render(request, 'stafflogin.html')

        # if request.GET.get('beingprepared'):
        #     x = request.GET['thisorder']
        #     x.delivery_status = "Updated"
        #     x.save()
        #     j = Order.objects.filter(id=x)
        #     j.delivery_status = "Updated"
        #     j.save()
        #     return render(request, 'stafflogin.html')

def currenttime():
    return datetime.datetime.now()

def updateorderstatus(request):
        if request.GET.get('beingprepared'):
            x = request.GET.get('beingprepared')
            item = Order.objects.get(id=x)
            timeofupdate = currenttime()
            item.delivery_status = "Order is now being prepared by our chefs"
            item.item_updated_at = timeofupdate
            item.save()
            return render(request, 'stafflogin.html', {'item': item})
        elif request.GET.get('onitsway'):
            x = request.GET.get('onitsway')
            item = Order.objects.get(id=x)
            timeofupdate = currenttime()
            item.delivery_status = "Order has left the restaurant and is currently being delivered"
            item.item_updated_at = timeofupdate
            item.save()
            return render(request, 'stafflogin.html', {'item': item})
        elif request.GET.get('delivered'):
            x = request.GET.get('delivered')
            item = Order.objects.get(id=x)
            timeofupdate = currenttime()
            item.delivery_status = "Order has successfully reached its destination"
            item.item_updated_at = timeofupdate
            item.save()
            return render(request, 'stafflogin.html', {'item': item})

# def add_to_order(request):
#     try:
#         cart = Cart.objects.filter(user=request.user)
#         if cart.exists():
#             manager1 = User.objects.get(id=1)
#             context = {'personalcart': cart}
#             date = datetime.datetime.today()
#             total_price = 0
#             for obj in cart:
#                 total_price += obj.price
#             address_line_1 = request.POST.get('address_line_1')
#             address_line_2 = request.POST.get('address_line_2')
#             address_town = request.POST.get('address_town')
#             order = Order.objects.create(user=obj.user, delivery_crew=manager1, status=False, total=total_price, date=date, address_line_1=address_line_1, address_line_2=address_line_2, address_town=address_town)
#             order.save()
#             for item in cart:
#                 i = OrderItem.objects.create(order=order, menuitem=item.menuitem, quantity=item.quantity, unit_price=item.unit_price, price=item.price)
#                 i.save()
#         # product.save()
#             Cart.objects.filter(user=request.user).delete()
#             order_data = Order.objects.filter(user=request.user)
#             for item in order_data:
#                 orderitems = OrderItem.objects.filter(order=item)
#             oi_data = {"orderitems": orderitems}
#             main_data = {"order": order_data}
#             messages.success(request, "Your order has been sent!")
#             return render(request, 'order.html', {'personalcart': context, "item": item, "i": i, "total_price": total_price, "order": main_data, "orderitems": oi_data})
#         else:
#             order_data = Order.objects.filter(user=request.user)
#             for item in order_data:
#                 orderitems = OrderItem.objects.filter(order=item)
#             oi_data = {"orderitems": orderitems}
#             main_data = {"order": order_data}
#             return render(request, 'order.html', {"order": main_data, "orderitems": oi_data})
#     except:
#         messages.info(request, "You don't currently have any orders pending, nor any items in your cart.")
#         messages.info(request, "Feel free to add items to your cart, and place an order when you are ready.")
#         messages.info(request, "With care, your LittleLemon team.")
#         return redirect('cart')






# def addaddresstoorder(request):
#     if request.method == 'PUT':
#         data = request.POST
#         order = Order.objects.get(user=CurrentUserField())
#         order.address_line_1 = request.POST.get('address_line_1')
#         order.address_line_2 = request.POST.get('address_line_2')
#         order.address_town = request.POST.get('address_town')
#         order.save()
#         messages.success('your address has been added')
#         return redirect('order')

# def add_to_order(request):
#     cart = Cart.objects.filter(user=request.user)
#     if cart.exists():
#         manager1 = User.objects.get(id=1)
#         context = {'personalcart': cart}
#         date = datetime.datetime.today()
#         total_price = 0
#         for obj in cart:
#             total_price += obj.price
#         order = Order.objects.create(user=obj.user, delivery_crew=manager1, status=False, total=total_price, date=date)
#         order.save()
#         for item in cart:
#             i = OrderItem.objects.create(order=order, menuitem=item.menuitem, quantity=item.quantity, unit_price=item.unit_price, price=item.price)
#             i.save()
#         # product.save()
#         Cart.objects.filter(user=request.user).delete()
#         order_data = Order.objects.filter(user=request.user)
#         for item in order_data:
#             orderitems = OrderItem.objects.filter(order=item)
#         oi_data = {"orderitems": orderitems}
#         main_data = {"order": order_data}
#         return render(request, 'order.html', {'personalcart': context, "item": item, "i": i, "total_price": total_price, "order": main_data, "orderitems": oi_data})
#     else:
#         order_data = Order.objects.filter(user=request.user)
#         if order_data.exists():
#             for item in order_data:
#                 orderitems = OrderItem.objects.filter(order=item)
#                 oi_data = {"orderitems": orderitems}
#                 main_data = {"order": order_data}
#                 return render(request, 'order.html', {"order": main_data, "orderitems": oi_data})






# def vieworder(request):
#     order_data = Order.objects.filter(user=request.user)
#     for item in order_data:
#         orderitems = OrderItem.objects.filter(order=item)
#         oi_data = {"orderitems": orderitems}
#         main_data = {"order": order_data}
#         return render(request, 'order.html', {"order": main_data, "orderitems": oi_data})

class IndividualOrderView(generics.ListCreateAPIView):
    serializer_class = IndividualOrderSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def get_permissions(self):
        order = Order.objects.get(pk=self.kwargs['pk'])

        if self.request.method == 'GET':
            if self.request.user == order.user:
                permission_classes = [IsAuthenticated]
            else:
                permission_classes = [IsDeliveryPersonnel | IsManager | IsAdminUser]
        elif self.request.method == 'PUT':
            permission_classes = [IsDeliveryPersonnel | IsManager | IsAdminUser]
        else:
            permission_classes = [IsManager | IsAdminUser]
        return [permission() for permission in permission_classes] 

    def get_queryset(self, **kwargs):
            queryset = OrderItem.objects.filter(order_id=self.kwargs['pk'])
            return queryset

    # Please use the user id of the desired delivery staff for the request
    def patch(self, request, **kwargs):
        serialized_item = PatchOrderSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)

        # Make sure that this is the staff member's user id number in the system, as that is their primary key, not their username
        order_id = self.kwargs['pk']

        delivery_personnel_id = request.data['delivery_crew'] 
        order = get_object_or_404(Order, pk=order_id)
        delivery_personnel = get_object_or_404(User, pk=delivery_personnel_id)
        order.delivery_crew = delivery_personnel
        assigned_deliverer = str(delivery_personnel.username)
        order_number = str(order.id)
        order.save()
        return JsonResponse(status=200, data={'AssignedDeliveryPersonnel': assigned_deliverer + ' has been assigned successfully to order #' + order_number})
    
    # Please type True or False with capital letters when updating the order status
    def put(self, request, **kwargs):
        status = request.data['status']
        order_id = self.kwargs['pk']
        order = get_object_or_404(Order, pk=order_id)
        order.status = status
        order_number = str(order.id)
        order.save()
        if order.status == 'True':
            return JsonResponse(status=200, data={'Order Status':'Order #'+ order_number + ' has been delivered successfully to its destination.'})
        return JsonResponse(status=200, data={'Order Status':'Order #'+ order_number + ' is undelivered at this time.'})

    def delete(self, request, **kwargs):
        order_id = self.kwargs['pk']
        order = Order.objects.get(pk=order_id)
        order_number = str(order.id)
        order.delete()
        return JsonResponse(status=200, data={'Update': 'Order #'+ order_number +' has been deleted.'})



# COMMENTS ///////////////////////////////////////////////////////////////

def CommentView(request):
    context = {}
    context['form'] = CommentForm()
    a = Comments()
    f = CommentForm(request.POST, instance=a)
    # messages.info(request, 'Please fill out the form, and we will read your message in due course.')
    if request.method == 'POST':
        if f.is_valid():
            f.save()
            messages.success(request, 'Thank you. Your comment has been sent successfully')
        else:
            messages.error(request, 'Something went wrong. Please try again.')

    return render(request, "comments.html", context)

# class CommentView(View):
#     form_class = CommentForm

#     def get(self, request):
#         form = self.form_class()
#         return render(request)
    
#     def data_inputted(self, form):
#         data = {
#             'name': form.cleaned_data.get('name'),
#             'comment': form.cleaned_data.get('comment'),
#         }
#         return data
    
#     def post(self, request):
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             data = self.data_inputted(form)
#         return render(request, "comments.html", context)
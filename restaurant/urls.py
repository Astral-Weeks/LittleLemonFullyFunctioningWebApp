from django.urls import path
from . import views
from.views import register


urlpatterns = [
    path('', views.home, name="home"),
    path('about/', views.about, name="about"),
    path('book/', views.book, name="book"),
    path('reservations/', views.reservations.as_view(), name="reservations"),
    path('menu/', views.menu, name="menu"),
    path('menu-item/<int:pk>/', views.display_menu_item, name="menu_item"),  
    #  unnecessary now    path('category', views.category, name="category"),
    path('bookings', views.bookings, name='bookings'),
    path('login-page/', views.login_user, name="login-page"),
    path('logout-page/', views.logout_user, name="logout-page"),
    path('categories', views.CategoriesView.as_view(), name="categories"),
    path('categories/<int:pk>', views.ViewByCategoryView.as_view()),
    path('managers', views.AllManagersView.as_view()),
    path('deliverypersonnel', views.AllDeliveryPersonnelView.as_view()),
    path('cart/', views.CartView.as_view(), name="cart"),
    path('add/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    # path('order/', views.vieworder, name="vieworder"),
    path('order/', views.add_to_order, name="order"),
    path('order/<int:pk>', views.IndividualOrderView.as_view()),
    path('comments/', views.CommentView, name="comments"),
    path('register', views.register.as_view(), name="register"),
    path('checkusername/', views.checkusername, name="checkusername"),
    path('addressfordelivery/', views.addressfordelivery, name="addressfordelivery"),
    path('stafflogin/', views.stafflogin.as_view(), name="stafflogin"),
    path('updateorderstatus/', views.updateorderstatus, name="updateorderstatus")
]
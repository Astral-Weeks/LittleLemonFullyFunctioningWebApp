# from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Booking
from .models import Comments


# Code added for loading form data on the Booking page
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["first_name", "reservation_date", "reservation_slot"]

# class CommentForm(forms.Form):
#     name = forms.CharField(max_length=255)
#     comment = forms.CharField(max_length=1000)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ["name", "comment"]

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email"]
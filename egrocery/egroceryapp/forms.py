from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name','last_name','username', 'email', 'password1', 'password2']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }

class ProfileRegisterForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["mobile_number",
            "Address",'pincode']
        labels = {
            'mobile_number': 'Mobile Number',
            'Address': 'Address',
            'pincode': 'Pincode',
        }


class AddToCartForm(forms.Form):
    productID = forms.CharField(max_length=255, widget=forms.HiddenInput())
    quantity = forms.CharField(max_length=255, widget=forms.HiddenInput())
    product_price = forms.CharField(max_length=255, widget=forms.HiddenInput())
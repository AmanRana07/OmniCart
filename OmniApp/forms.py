from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Customer




class CustomerCreationForm(UserCreationForm):
    class Meta:
        model = Customer
        fields = (
            "email",
            "username",
            "user_type",
            "full_name",
            "address",
            "phone_number",
        )
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "user_type": forms.Select(attrs={"class": "form-select"}),
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
        }


class CustomerChangeForm(UserChangeForm):
    class Meta:
        model = Customer
        fields = (
            "email",
            "username",
            "user_type",
            "full_name",
            "address",
            "phone_number",
        )
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "user_type": forms.Select(attrs={"class": "form-select"}),
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
        }

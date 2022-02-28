from django import forms
from . import models
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import *


class ProductForm(ModelForm):

    class Meta:
        model = AuctionListing
        fields= '__all__'
        exclude=('user', 'active',)
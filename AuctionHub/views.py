from django.urls import reverse
from django.db.models import Max
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render
from django.db import IntegrityError
from .forms import *
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .models import User, Category, AuctionListing, Bid, Comment
import razorpay
import os
from dotenv import load_dotenv
import pathlib

path = pathlib.Path().absolute() / 'mysite/.env'
load_dotenv(dotenv_path=path)

def index(request):
    obj = AuctionListing.objects.filter(active=True)
    return render(request, "AuctionHub/auctions.html", {
        "objects": obj
    })


def all(request):
    obj = AuctionListing.objects.all()
    return render(request, "AuctionHub/auctions.html", {
        "objects": obj
    })


def login_view(request):
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("userpage"))
        else:
            return render(request, "AuctionHub/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "AuctionHub/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("dashboard"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "AuctionHub/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "AuctionHub/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("userpage"))
    else:
        return render(request, "AuctionHub/register.html")


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        print("POST")
        for field in form:
            print("Field Error:", field.name,  field.errors)
        if form.is_valid():
            print("valid")
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            print(instance)
            form = ProductForm()  
            categories = Category.objects.all()           
            return redirect('categories')
    form = ProductForm()
    return render(request, 'AuctionHub/add_product.html', {'form': form})
  

@login_required
def details(request, id):
    item = AuctionListing.objects.get(id=id)
    bids = Bid.objects.filter(auctionListing=item)
    comments = Comment.objects.filter(auctionListing=item)
    value = bids.aggregate(Max('bidValue'))['bidValue__max']
    bid = None
    
    if value is not None:
        bid = Bid.objects.filter(bidValue=value)[0]

    client = razorpay.Client(auth=(os.environ.get('api_key'), os.environ.get('secret')))

    order_amount = "150000"
    order_currency = 'INR'
    order_receipt = 'order_rcptid_11'
    notes = {'Shipping address': 'Bommanahalli, Bangalore'}   # OPTIONAL

    payment_order = client.order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt, notes=notes,payment_capture=1))
    payment_order_id = payment_order['id']
    return render(request, "AuctionHub/details.html", {
        'item': item,
        'bids': bids,
        'comments': comments,
        'bid': bid,
        'api_key': os.environ.get('api_key'), 'order_id': payment_order_id
    })

@login_required
def categories(request):
    if request.method == 'POST':
        category = request.POST["category"]
        new_category, created = Category.objects.get_or_create(
            name=category.lower())
        if created:
            new_category.save()
        else:
            messages.warning(request, "Category already Exists!")
        return HttpResponseRedirect(reverse("categories"))
    return render(request, "AuctionHub/categories.html", {
        'categories': Category.objects.all()
    })

@login_required
def filter(request, name):
    category = Category.objects.get(name=name)
    obj = AuctionListing.objects.filter(category=category)
    return render(request, "AuctionHub/auctions.html", {
        "objects": obj
    })


@login_required
def userpage(request):
    return render(request, "AuctionHub/userpage.html")

def dashboard(request):
    return render(request, "AuctionHub/dashboard.html")
@login_required
def comment(request, id):
    if request.method == 'POST':
        auctionListing = AuctionListing.objects.get(id=id)
        user = request.user
        commentValue = request.POST["content"].strip()
        if(commentValue != ""):
            comment = Comment.objects.create(date=timezone.now(
            ), user=user, auctionListing=auctionListing, commentValue=commentValue)
            comment.save()
        return HttpResponseRedirect(reverse("details", kwargs={'id': id}))
    return HttpResponseRedirect(reverse("index"))

@login_required
def mybids(request):
    obj = AuctionListing.objects.filter(active=True)
    return render(request, "AuctionHub/mybids.html", {
        "objects": obj
    })

@login_required
def bid(request, id):
    if request.method == 'POST':
        auctionListing = AuctionListing.objects.get(id=id)
        bidValue = request.POST["bid"]
        args = Bid.objects.filter(auctionListing=auctionListing)
        value = args.aggregate(Max('bidValue'))['bidValue__max']
        if value is None:
            value = 0
        if float(bidValue) < auctionListing.startBid or float(bidValue) <= value:
            messages.warning(
                request, f'Bid Higher than: {max(value, auctionListing.startBid)}!')
            return HttpResponseRedirect(reverse("details", kwargs={'id': id}))
        user = request.user
        bid = Bid.objects.create(
            date=timezone.now(), user=user, bidValue=bidValue, auctionListing=auctionListing)
        bid.save()
    return HttpResponseRedirect(reverse("details", kwargs={'id': id}))


@login_required
def end(request, itemId):
    auctionListing = AuctionListing.objects.get(id=itemId)
    user = request.user
    if auctionListing.user == user:
        auctionListing.active = False
        auctionListing.save()
        messages.success(
            request, f'Auction for {auctionListing.name} successfully closed!')
    else:
        messages.info(
            request, 'You are not authorized to end this listing!')
    return HttpResponseRedirect(reverse("details", kwargs={'id': itemId}))


@login_required
def watchlist(request):
    if request.method == 'POST':
        user = request.user
        auctionListing = AuctionListing.objects.get(id=request.POST["item"])
        if request.POST["status"] == '1':
            user.watchlist.add(auctionListing)
        else:
            user.watchlist.remove(auctionListing)
        user.save()
        return HttpResponseRedirect(
            reverse("details", kwargs={'id': auctionListing.id}))
    return HttpResponseRedirect(reverse("index"))


@login_required
def watch(request):
    user = request.user
    obj = user.watchlist.all()
    return render(request, "AuctionHub/auctions.html", {
        "objects": obj
    })

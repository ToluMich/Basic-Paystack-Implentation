from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from payment_app.models import UserWallet
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.create(username=username, password=password)
        UserWallet.objects.create(user=user)
        return render(request, "register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('initiate_payment')
        else:
            return redirect('login')

    return render(request, 'login.html')

@login_required(login_url="login")
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url="login")
def checkout_section(request):
    return render(request, "payment.html")
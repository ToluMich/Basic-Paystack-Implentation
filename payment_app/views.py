from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Payment
from .paystack import Paystack
import json
import requests

paystack = Paystack()

@login_required(login_url="login")
def initiate_payment(request):
    if request.method == "POST":
        amount = request.POST.get('amount')
        email = request.user.email

        # Create a payment record
        payment = Payment.objects.create(user=request.user, amount=amount, email=email)

        # Redirect to Paystack payment page
        # return redirect(f"https://checkout.paystack.com/transaction/initialize?reference={payment.ref}&amount={amount}&email={email}")
        
        url = f"https://checkout.paystack.com/transaction/initialize?reference={payment.ref}&amount={amount}&email={email}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_PUBLIC_KEY}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers)

        return redirect('verify_payment', ref=payment.ref)

    return render(request, 'initiate_payment.html')


import requests
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse


import requests
import json
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import Transaction
from django.views.decorators.csrf import csrf_exempt



def initialize_payment(request):
    if request.method == 'POST':
        email = request.user.email
        # email = request.POST.get('email')
        amount = request.POST.get('amount')
        amount_in_kobo = int(float(amount) * 100)  # Convert to kobo

        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json',
        }

        # base_url = request.build_absolute_uri('')  
        base_url = request.build_absolute_uri('/')[:-1]  #This part returns only 'http://127.0.0.1:8000/'
        webhook_url = redirect('webhook')
        the_callback_url = redirect('the_callback')
        data = {
            'email': email,
            'amount': amount_in_kobo,
            'callback_url': base_url + the_callback_url.url,  # Change to your callback URL
            # 'metadata': {
            #     'webhook_url': base_url + webhook_url.url,  # Your webhook URL
            # }
            # 'callback_url': 'https://yourdomain.com/pay/callback/',  # Change to your callback URL
        }

        response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, json=data)
        response_data = response.json()

        if response_data['status']:
            # Save transaction to the database
            transaction = Transaction.objects.create(
                email=email,
                amount=amount,
                reference=response_data['data']['reference'],
                status='pending'
            )
            return redirect(response_data['data']['authorization_url'])
        return JsonResponse({'error': response_data['message']})
    return JsonResponse({'error': 'Invalid request'}, status=400)

  

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        event = data['event']
        if event == 'charge.success':
            reference = data['data']['reference']
            try:
                transaction = Transaction.objects.get(reference=reference)
                transaction.status = 'successful'
                transaction.save()
            except Transaction.DoesNotExist:
                return JsonResponse({'error': 'Transaction not found'}, status=404)
        return JsonResponse({'status': 'success'}, status=200)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def the_callback(request):
    if request.method == 'GET':
        return render(request, "payment_success.html")
    return JsonResponse({'error': 'Invalid request'}, status=400)
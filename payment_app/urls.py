from django.urls import path
from . import views

urlpatterns = [
    path('initiate/', views.initiate_payment, name='initiate_payment'),
    path('initialize/', views.initialize_payment, name='initialize_payment'),
    path('pay/callback/', views.the_callback, name='the_callback'),
    path('pay/webhook/', views.webhook, name='webhook'),
]
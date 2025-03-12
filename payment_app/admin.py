from django.contrib import admin

from payment_app.models import *

# Register your models here.
admin.site.register(UserWallet)
admin.site.register(Payment)
admin.site.register(Transaction)
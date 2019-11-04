from django.urls import path
from views import *

app_name = 'payment'

urlpatterns = [
    path('callback/', callback, name='callback'),
    path('view/', view_payments, name='view_payments'),
]

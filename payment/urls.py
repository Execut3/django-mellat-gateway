from django.conf.urls import url
from views import *


urlpatterns = [
    url(r'^callback$', callback, name='callback'),
    url(r'^view$', view_payments, name='view_payments'),
]

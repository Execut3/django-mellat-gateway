# -*- coding: utf-8 -*-
from random import randint

try:
    from django.contrib.contenttypes import fields as generic
except ImportError:
    from django.contrib.contenttypes import generic

from django.contrib.contenttypes.models import ContentType
from django.db import models

from django.contrib.auth import User


class PaymentTransaction(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    amount = models.PositiveIntegerField()
    transaction_date = models.DateTimeField(auto_now_add=True)

    success = models.BooleanField(default=False)
    error_code = models.IntegerField(default=0)
    error_description = models.CharField(max_length=300, blank=True,
                                         default='درخواست شروع پرداخت برای بانک ارسال شده است.')

    order_id = models.BigIntegerField(default=0)

    RefId = models.CharField(max_length=40, null=True, blank=True)
    ResCode = models.IntegerField(null=True, blank=True)
    SaleOrderId = models.CharField(max_length=40, null=True, blank=True)
    SaleReferenceId = models.CharField(max_length=40, null=True, blank=True)

    item_content_type = models.ForeignKey(
        ContentType,
        verbose_name='content page',
        null=True,
        blank=True,
    )
    item_object_id = models.PositiveIntegerField(
        verbose_name='related object',
        null=True,
    )
    content_object = generic.GenericForeignKey('item_content_type', 'item_object_id')

    def __unicode__(self):
        return 'خرید برای کاربر %s' % self.user.username

    class Meta:
        db_table = 'payment_transaction'

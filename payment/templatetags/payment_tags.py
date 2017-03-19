# -*- coding: utf-8 -*-

from django import template
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def render_purchased_item_info(payment):
    result = ''
    o_type = ContentType.objects.filter(pk=payment.item_content_type_id).first()
    if o_type:
        o_instance = o_type.model_class().objects.filter(pk=payment.item_object_id).first()
        # Print whatever you want to show to users based on the o_instance (the object that you assigned for payment)
    else:
        result = 'آیتم ثبت نشده است.'
    return mark_safe(result)

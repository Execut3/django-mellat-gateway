# -*- coding: utf-8 -*-
from datetime import datetime
from random import randint

from django.contrib.contenttypes.models import ContentType
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.core.paginator import Paginator
from django.shortcuts import render_to_response
from django.template import RequestContext
from suds.client import Client

from panel.utils import purchase_this_item
from payment.models import PaymentTransaction

terminalID = long(XXXXX)
userName = 'XXXXXX'
userPassword = 'XXXXX'
operational_wsdl_url = 'https://bpm.shaparak.ir/pgwchannel/services/pgw?wsdl'
callback_url = 'http://xxx.xxx.xxx.xxx/payment/callback'


def callback(request):
    CardHolderPan = request.POST.get('CardHolderPan', '')
    CardHolderInfo = request.POST.get('CardHolderInfo', '')
    ResCode = request.POST.get('ResCode', None)
    SaleReferenceId = request.POST.get('SaleReferenceId', None)
    SaleOrderId = request.POST.get('SaleOrderId', None)
    RefId = request.POST.get('RefId', None)

    status = False
    message = ''
    if RefId:
        payment_transaction = PaymentTransaction.objects.filter(RefId=RefId).first()
        payment_transaction.ResCode = int(ResCode)
        payment_transaction.SaleOrderId = SaleOrderId
        payment_transaction.SaleReferenceId = SaleReferenceId

        if ResCode:
            status, message = res_code_status(int(ResCode))
            if status:

                order_id = randint(1, 999999999999)
                client = Client(operational_wsdl_url)
                result = client.service.bpVerifyRequest(terminalID, userName, userPassword,
                                                        int(order_id), int(SaleOrderId), int(SaleReferenceId))
                try:
                    ResCode = int(result)
                    status, message = res_code_status(int(ResCode))
                except:
                    pass

                if status:
                    payment_transaction.success = True
                    purchase_item_status, purchased_item = purchase_this_item(payment_transaction)
                else:
                    print 'got something that i didnt count on it!'

            else:
                payment_transaction.error_code = int(ResCode)
                payment_transaction.error_description = message
        payment_transaction.save()

    return render_to_response('payment/callback.html', locals(), RequestContext(request))


def set_negotiation_for_payment(request, price, item):
    local_date = datetime.now().strftime("%Y%m%d")
    local_time = datetime.now().strftime("%H%M%S")
    client = Client(operational_wsdl_url)

    order_id = randint(1, 999999999999)

    result = client.service.bpPayRequest(terminalID, userName, userPassword, order_id, int(price) * 10,
                                         str(local_date), str(local_time), '', callback_url, 0)
    res_code = int(result.split(',')[0].strip())
    status, message = res_code_status(res_code)
    ref_id = 0
    if status:
        ref_id = result.split(',')[1].strip()

    user = request.user
    PaymentTransaction.objects.get_or_create(user=user, order_id=order_id, amount=int(price), RefId=ref_id,
                                             item_content_type=ContentType.objects.get_for_model(item),
                                             item_object_id=item.pk)
    print result
    return status, message, ref_id


def res_code_status(res_code):
    if res_code == 0:
        return True, 'تراکنش با موفقیت انجام شد.'
    elif res_code == 11:
        return False, 'شماره کارت نامعتبر است.'
    elif res_code == 12:
        return False, 'موجودی کافی نیست.'
    elif res_code == 13:
        return False, 'رمز نادرست است.'
    elif res_code == 14:
        return False, 'تعداد دفعات وارد کردن رمز بیش از حد مجاز است.'
    elif res_code == 15:
        return False, 'کارت نامعتبر است.'
    elif res_code == 16:
        return False, 'دفعات برداشت وجه بیش از حد مجاز است.'
    elif res_code == 17:
        return False, 'کاربر از انجام تراکنش منصرف شده است.'
    elif res_code == 18:
        return False, 'تاریخ انقضای کارت گذشته است.'
    elif res_code == 19:
        return False, 'مبلغ برداشت وجه بیش از حد مجاز است.'
    elif res_code == 111:
        return False, 'صادر کننده کارت نامعتبر است.'
    elif res_code == 112:
        return False, 'خطای سوییچ صادر کننده کارت'
    elif res_code == 113:
        return False, 'پاسخصی از صادر کننده کارت دریافت نشد.'
    elif res_code == 114:
        return False, 'دارنده کارت مجاز به انجام تراکنش نیست.'
    elif res_code == 21:
        return False, 'پذیرنده نامعتبر است.'
    elif res_code == 23:
        return False, 'خطای امنیتی رخ داده است.'
    elif res_code == 24:
        return False, 'اطلاعات کاربری پذیرنده نامعتبر است.'
    elif res_code == 25:
        return False, 'مبلغ نامعتبر است.'
    elif res_code == 31:
        return False, 'پاسخ نامعتبر است.'
    elif res_code == 32:
        return False, 'فرمت اطلاعات وارد شده صحیح نمی‌باشد.'
    elif res_code == 33:
        return False, 'حساب نامعتبر است.'
    elif res_code == 34:
        return False, 'خطای سیستمی'
    elif res_code == 35:
        return False, 'تاریخ نامعتبر است.'
    elif res_code == 41:
        return False, 'شماره درخواست تکراری است.'
    elif res_code == 42:
        return False, 'تراکنش sale یافت نشد.'
    elif res_code == 43:
        return False, 'قبلا درخواست verify داده شده است.'
    elif res_code == 44:
        return False, 'درخواست verify یافت نشد.'
    elif res_code == 45:
        return False, 'تراکنش settle شده است.'
    elif res_code == 46:
        return False, 'تراکنش settle نشده است.'
    elif res_code == 47:
        return False, 'تراکنش settle یافت نشد.'
    elif res_code == 48:
        return False, 'تراکنش reverse شده است.'
    elif res_code == 49:
        return False, 'تراکنش refund یافت نشد.'
    elif res_code == 412:
        return False, 'شناسه قبض نادرست است.'
    elif res_code == 413:
        return False, 'شناسه پرداخت نادرست است.'
    elif res_code == 414:
        return False, 'سازمان صادر کننده قبض نامعتبر است.'
    elif res_code == 415:
        return False, 'زمان جلسه کاری به پایان رسیده است.'
    elif res_code == 416:
        return False, 'خطا در ثبت اطلاعات'
    elif res_code == 417:
        return False, 'شناسه پرداخت کننده نامعتبر است.'
    elif res_code == 418:
        return False, 'اشکال در تعریف اطلاعات مشتری'
    elif res_code == 419:
        return False, 'تعداد دفعات ورود به اطلاعات از حد مجاز گذشته است.'
    elif res_code == 421:
        return False, 'ip نامعتبر است.'
    elif res_code == 51:
        return False, 'تراکنش تکراری است.'
    elif res_code == 54:
        return False, 'تراکنش مرجع موجود نیست.'
    elif res_code == 55:
        return False, 'تراکنش نامعتبر است.'
    elif res_code == 61:
        return False, 'خطا در واریز'


def view_payments(request):
    payments = PaymentTransaction.objects.all().order_by('-transaction_date')
    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1
    paginator = Paginator(payments, 15)
    try:
        payments = paginator.page(page)
    except PageNotAnInteger:
        payments = paginator.page(1)
    except EmptyPage:
        payments = paginator.page(paginator.num_pages)
    return render_to_response('payment/view.html', locals(), RequestContext(request))

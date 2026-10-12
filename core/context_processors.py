from django.conf import settings


def site_info(request):
    phone = settings.SITE_PHONE
    return {
        'site_name': settings.SITE_NAME,
        'site_phone': phone,
        'site_phone_href': 'tel:' + phone.replace(' ', ''),
        'site_email': settings.SITE_EMAIL,
        'site_address': settings.SITE_ADDRESS,
        'site_opening_hours': settings.SITE_OPENING_HOURS,
    }

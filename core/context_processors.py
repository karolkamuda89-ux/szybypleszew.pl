from datetime import date

from django.conf import settings


def site_info(request):
    phone = settings.SITE_PHONE
    digits = phone.replace(' ', '')
    if not digits.startswith('+'):
        digits = '+48' + digits
    return {
        'site_name': settings.SITE_NAME,
        'site_company': settings.SITE_COMPANY,
        'site_nip': settings.SITE_NIP,
        'site_founded': settings.SITE_FOUNDED,
        'site_years': date.today().year - settings.SITE_FOUNDED,
        'site_phone': phone,
        'site_phone_e164': digits,
        'site_phone_href': 'tel:' + digits,
        'site_email': settings.SITE_EMAIL,
        'site_street': settings.SITE_STREET,
        'site_postcode': settings.SITE_POSTCODE,
        'site_city': settings.SITE_CITY,
        'site_address': f'{settings.SITE_STREET}, {settings.SITE_POSTCODE} {settings.SITE_CITY}',
        'site_hours_weekdays': settings.SITE_HOURS_WEEKDAYS,
        'site_hours_saturday': settings.SITE_HOURS_SATURDAY,
    }

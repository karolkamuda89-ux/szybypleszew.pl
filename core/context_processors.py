"""Context processor z danymi firmy.

Funkcja `site_info` jest wywolywana przy renderowaniu kazdego szablonu (zarejestrowana
w settings.TEMPLATES), dzieki czemu w HTML-u mozna uzywac np. {{ site_phone }}
bez przekazywania tych danych w kazdym widoku. Same dane zmienia sie w config/settings.py.
"""
from datetime import date

from django.conf import settings


def site_info(request):
    phone = settings.SITE_PHONE
    # Numer w formacie miedzynarodowym (+48...) – potrzebny do linku tel: i danych dla Google.
    digits = phone.replace(' ', '')
    if not digits.startswith('+'):
        digits = '+48' + digits
    return {
        'site_name': settings.SITE_NAME,
        'site_company': settings.SITE_COMPANY,
        'site_nip': settings.SITE_NIP,
        'site_founded': settings.SITE_FOUNDED,
        # Liczba lat na rynku liczy sie sama, nie trzeba jej co roku poprawiac
        'site_years': date.today().year - settings.SITE_FOUNDED,
        'site_phone': phone,                 # do wyswietlania, np. "607 560 682"
        'site_phone_e164': digits,           # np. "+48607560682"
        'site_phone_href': 'tel:' + digits,  # do przyciskow "Zadzwon"
        'site_email': settings.SITE_EMAIL,
        'site_email_alt': settings.SITE_EMAIL_ALT,
        'site_street': settings.SITE_STREET,
        'site_postcode': settings.SITE_POSTCODE,
        'site_city': settings.SITE_CITY,
        'site_address': f'{settings.SITE_STREET}, {settings.SITE_POSTCODE} {settings.SITE_CITY}',
        'site_hours_weekdays': settings.SITE_HOURS_WEEKDAYS,
        'site_hours_saturday': settings.SITE_HOURS_SATURDAY,
        'site_facebook': settings.SITE_FACEBOOK,
        'site_author': settings.SITE_AUTHOR,
        # Link do wizytowki Google – ikona w stopce
        'site_google_maps': settings.GOOGLE_REVIEWS_URL,
    }

"""Widoki strony firmowej.

Dane firmy (telefon, adres, godziny) trafiaja do kazdego szablonu automatycznie
przez context processor `core.context_processors.site_info`, wiec widoki przekazuja
tylko to, co jest potrzebne na konkretnej stronie.
"""
from django.shortcuts import render

from .google_reviews import get_google_reviews


def home(request):
    """Strona glowna. Dodatkowo przekazuje ocene i opinie z wizytowki Google."""
    return render(request, 'core/home.html', {'google': get_google_reviews()})


def blog(request):
    """Podstrona bloga (na razie z zapowiedziami wpisow)."""
    return render(request, 'core/blog.html')

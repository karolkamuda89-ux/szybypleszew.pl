"""Widoki strony firmowej.

Dane firmy (telefon, adres, godziny) trafiaja do kazdego szablonu automatycznie
przez context processor `core.context_processors.site_info`, wiec widoki przekazuja
tylko to, co jest potrzebne na konkretnej stronie.
"""
from django.shortcuts import render

from .gallery import GALLERY, GALLERY_VISIBLE, PHOTO_ABOUT, PHOTO_HERO
from .google_reviews import get_google_reviews


def home(request):
    """Strona glowna: opinie z Google, galeria realizacji i zdjecia firmy."""
    return render(request, 'core/home.html', {
        'google': get_google_reviews(),
        'gallery': GALLERY,
        'gallery_visible': GALLERY_VISIBLE,
        'gallery_hidden_count': max(len(GALLERY) - GALLERY_VISIBLE, 0),
        'photo_hero': PHOTO_HERO,
        'photo_about': PHOTO_ABOUT,
    })


def blog(request):
    """Podstrona bloga (na razie z zapowiedziami wpisow)."""
    return render(request, 'core/blog.html')

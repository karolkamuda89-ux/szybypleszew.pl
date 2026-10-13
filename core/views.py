"""Widoki strony firmowej.

Dane firmy (telefon, adres, godziny) trafiaja do kazdego szablonu automatycznie
przez context processor `core.context_processors.site_info`, wiec widoki przekazuja
tylko to, co jest potrzebne na konkretnej stronie.
"""
from django.db.models import Prefetch
from django.shortcuts import render

from .gallery import GALLERY_VISIBLE, PHOTO_ABOUT, PHOTO_HERO
from .google_reviews import get_google_reviews
from .models import GalleryItem, GalleryPhoto


def home(request):
    """Strona glowna: opinie z Google, galeria realizacji (z bazy, edytowana w panelu) i zdjecia firmy."""
    items = (GalleryItem.objects.filter(is_published=True)
             .prefetch_related(Prefetch('photos', queryset=GalleryPhoto.objects.order_by('order', 'pk'))))
    # Realizacje bez zdjec pomijamy – pusty kafelek nic by nie pokazal
    gallery = [item for item in items if item.photos.all()]
    return render(request, 'core/home.html', {
        'google': get_google_reviews(),
        'gallery': gallery,
        'gallery_visible': GALLERY_VISIBLE,
        'gallery_hidden_count': max(len(gallery) - GALLERY_VISIBLE, 0),
        'photo_hero': PHOTO_HERO,
        'photo_about': PHOTO_ABOUT,
    })


def blog(request):
    """Podstrona bloga (na razie z zapowiedziami wpisow)."""
    return render(request, 'core/blog.html')

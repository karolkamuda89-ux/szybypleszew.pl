"""Testy strony. Uruchomienie: python manage.py test"""
from unittest import mock

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from .google_reviews import get_google_reviews

# Przykladowa odpowiedz Google Places API – testy nie lacza sie z prawdziwym Google.
# Zawiera opinie dobra, slaba (2 gwiazdki) i bez tresci, zeby sprawdzic filtrowanie.
PLACES_RESPONSE = {
    'rating': 4.7,
    'userRatingCount': 251,
    'googleMapsUri': 'https://maps.google.com/?cid=1',
    'reviews': [
        {'rating': 5, 'text': {'text': 'Super szybka wymiana szyby.'},
         'relativePublishTimeDescription': 'tydzień temu',
         'authorAttribution': {'displayName': 'Jan K.', 'uri': 'https://g.co/u/1', 'photoUri': ''}},
        {'rating': 2, 'text': {'text': 'Słaba obsługa.'},
         'authorAttribution': {'displayName': 'Ktoś'}},
        {'rating': 5, 'text': {'text': ''},
         'authorAttribution': {'displayName': 'Bez tekstu'}},
    ],
}


class HomePageTests(TestCase):
    """Strona glowna: czy sie otwiera i czy zawiera kluczowe elementy."""

    def test_home_page_returns_200(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_header_has_call_to_action(self):
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, 'href="tel:+48607560682"')

    def test_contact_shows_both_emails(self):
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, 'mailto:szybypleszew@interia.pl')
        self.assertContains(response, 'mailto:autoszybypleszew@interia.pl')

    def test_home_shows_visee_wipers(self):
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, 'id="wycieraczki"')


class GalleryTests(TestCase):
    """Galeria: kazde zdjecie z core/gallery.py ma pliki w media/ i trafia na strone."""

    def test_gallery_files_exist(self):
        from pathlib import Path
        from django.conf import settings
        from .gallery import GALLERY, PHOTO_ABOUT, PHOTO_HERO
        media = Path(settings.MEDIA_ROOT)
        # media/ nie jest w repozytorium (.gitignore) – na swiezej kopii bez zdjec pomijamy test
        if not (media / 'galeria').exists():
            self.skipTest('brak folderu media/galeria (zdjecia nie sa w repozytorium)')
        for foto in GALLERY:
            self.assertTrue((media / 'galeria' / f"{foto['plik']}.webp").exists(), foto['plik'])
            self.assertTrue((media / 'galeria' / 'min' / f"{foto['plik']}.webp").exists(), foto['plik'])
        self.assertTrue((media / PHOTO_HERO).exists())
        self.assertTrue((media / PHOTO_ABOUT).exists())

    def test_home_shows_gallery_and_hides_extra_photos(self):
        from .gallery import GALLERY, GALLERY_VISIBLE
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, 'class="gallery-link"', count=len(GALLERY))
        self.assertContains(response, ' hidden>', count=len(GALLERY) - GALLERY_VISIBLE)
        self.assertContains(response, 'id="gallery-more"')


class BlogPageTests(TestCase):
    """Podstrona bloga."""

    def test_blog_page_returns_200(self):
        response = self.client.get(reverse('core:blog'))
        self.assertEqual(response.status_code, 200)


class GoogleReviewsTests(TestCase):
    """Pobieranie opinii Google: dane zapasowe, filtrowanie, cache i obsluga bledow."""

    def setUp(self):
        # Czyscimy cache, zeby wynik jednego testu nie wplywal na kolejny
        cache.clear()

    @override_settings(GOOGLE_PLACES_API_KEY='', GOOGLE_PLACE_ID='')
    def test_without_api_key_uses_fallback(self):
        data = get_google_reviews()
        self.assertEqual(data['rating'], 4.8)
        self.assertEqual(data['count'], 250)
        self.assertEqual(data['reviews'], [])

    @override_settings(GOOGLE_PLACES_API_KEY='key', GOOGLE_PLACE_ID='place')
    def test_only_good_reviews_with_text_are_shown(self):
        with mock.patch('core.google_reviews._fetch', return_value=PLACES_RESPONSE) as fetch:
            data = get_google_reviews()
            get_google_reviews()
        self.assertEqual(fetch.call_count, 1)  # drugi raz z cache
        self.assertEqual(data['rating'], 4.7)
        self.assertEqual(data['count'], 251)
        self.assertEqual([r['author'] for r in data['reviews']], ['Jan K.'])
        self.assertIn('placeid=place', data['write_url'])

    @override_settings(GOOGLE_PLACES_API_KEY='key', GOOGLE_PLACE_ID='place')
    def test_api_error_falls_back(self):
        import urllib.error
        with mock.patch('core.google_reviews._fetch', side_effect=urllib.error.URLError('down')):
            data = get_google_reviews()
        self.assertEqual(data['rating'], 4.8)
        self.assertEqual(data['reviews'], [])

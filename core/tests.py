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


def make_image(name='zdjecie.jpg', size=(3000, 2000), fmt='JPEG'):
    """Tworzy w pamieci przykladowy obraz do wgrania (jak plik z telefonu)."""
    from io import BytesIO
    from PIL import Image
    from django.core.files.uploadedfile import SimpleUploadedFile
    buffer = BytesIO()
    Image.new('RGB', size, (120, 180, 40)).save(buffer, fmt)
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/jpeg')


class GalleryTests(TestCase):
    """Galeria w bazie: konwersja zdjec, wyswietlanie na stronie i panel admina."""

    def setUp(self):
        # Pliki testowe trafiaja do tymczasowego folderu, nie do prawdziwego media/
        import tempfile
        self.media = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media)
        self.override.enable()

    def tearDown(self):
        import shutil
        self.override.disable()
        shutil.rmtree(self.media, ignore_errors=True)

    def test_uploaded_photo_is_converted_to_webp_with_thumbnail(self):
        from PIL import Image
        from .models import GalleryItem, GalleryPhoto
        item = GalleryItem.objects.create(title='BMW – wymiana szyby')
        photo = GalleryPhoto.objects.create(item=item, image=make_image('Moje Zdjęcie.JPG'))
        self.assertTrue(photo.image.name.endswith('.webp'))
        self.assertTrue(photo.thumbnail.name.startswith('galeria/min/'))
        with Image.open(photo.image.path) as big, Image.open(photo.thumbnail.path) as small:
            self.assertEqual(big.format, 'WEBP')
            self.assertEqual(max(big.size), 1920)
            self.assertEqual(max(small.size), 800)

    def test_replacing_and_deleting_photo_removes_old_files(self):
        import os
        from .models import GalleryItem, GalleryPhoto
        item = GalleryItem.objects.create(title='Audi')
        photo = GalleryPhoto.objects.create(item=item, image=make_image('a.jpg'))
        old_paths = [photo.image.path, photo.thumbnail.path]
        photo.image = make_image('b.jpg')
        photo.save()
        self.assertFalse(any(os.path.exists(p) for p in old_paths))
        new_paths = [photo.image.path, photo.thumbnail.path]
        photo.delete()
        self.assertFalse(any(os.path.exists(p) for p in new_paths))

    def test_home_shows_items_with_multiple_photos(self):
        from .models import GalleryItem, GalleryPhoto
        item = GalleryItem.objects.create(title='Tesla – wymiana szyby')
        GalleryPhoto.objects.create(item=item, image=make_image('1.jpg'), caption='Demontaż', order=1)
        GalleryPhoto.objects.create(item=item, image=make_image('2.jpg'), caption='Montaż', order=2)
        GalleryItem.objects.create(title='Bez zdjęć')                       # pusta – pomijana
        GalleryItem.objects.create(title='Ukryta', is_published=False)      # niewidoczna
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, 'Tesla – wymiana szyby')
        self.assertContains(response, 'class="gallery-link', count=2)
        self.assertContains(response, '1 / 2')
        self.assertNotContains(response, 'Bez zdjęć')
        self.assertNotContains(response, 'Ukryta')

    def test_admin_can_add_item_with_several_photos_at_once(self):
        from django.contrib.auth.models import User
        from .models import GalleryItem
        admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'haslo-testowe')
        self.client.force_login(admin_user)
        self.assertEqual(self.client.get('/admin/core/galleryitem/').status_code, 200)
        response = self.client.post('/admin/core/galleryitem/add/', {
            'title': 'Mercedes – cały proces',
            'shape': 'szerokie',
            'order': 5,
            'is_published': 'on',
            'new_photos': [make_image('1.jpg'), make_image('2.jpg'), make_image('3.jpg')],
            # pusty formularz zdjec pod spodem (inline)
            'photos-TOTAL_FORMS': '0', 'photos-INITIAL_FORMS': '0',
            'photos-MIN_NUM_FORMS': '0', 'photos-MAX_NUM_FORMS': '1000',
        })
        self.assertEqual(response.status_code, 302, getattr(response, 'context', None) and response.context['adminform'].form.errors)
        item = GalleryItem.objects.get(title='Mercedes – cały proces')
        self.assertEqual(item.photos.count(), 3)
        self.assertEqual(self.client.get(f'/admin/core/galleryitem/{item.pk}/change/').status_code, 200)


class GalleryDeleteTests(TestCase):
    """Usuwanie w panelu: realizacja (pojedynczo i zbiorczo) znika razem z plikami zdjec."""

    def setUp(self):
        import tempfile
        from django.contrib.auth.models import User
        self.media = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media)
        self.override.enable()
        self.client.force_login(User.objects.create_superuser('admin', 'admin@example.com', 'haslo-testowe'))

    def tearDown(self):
        import shutil
        self.override.disable()
        shutil.rmtree(self.media, ignore_errors=True)

    def _item_with_photo(self, title):
        from .models import GalleryItem, GalleryPhoto
        item = GalleryItem.objects.create(title=title)
        photo = GalleryPhoto.objects.create(item=item, image=make_image())
        return item, [photo.image.path, photo.thumbnail.path]

    def test_list_has_delete_button(self):
        item, _ = self._item_with_photo('Do usunięcia')
        response = self.client.get('/admin/core/galleryitem/')
        self.assertContains(response, f'/admin/core/galleryitem/{item.pk}/delete/')

    def test_delete_single_item_removes_photo_files(self):
        import os
        from .models import GalleryItem
        item, paths = self._item_with_photo('Pojedyncza')
        response = self.client.post(f'/admin/core/galleryitem/{item.pk}/delete/', {'post': 'yes'})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(GalleryItem.objects.filter(pk=item.pk).exists())
        self.assertFalse(any(os.path.exists(p) for p in paths))

    def test_bulk_delete_action(self):
        import os
        from .models import GalleryItem
        a, paths_a = self._item_with_photo('A')
        b, paths_b = self._item_with_photo('B')
        response = self.client.post('/admin/core/galleryitem/', {
            'action': 'delete_selected', '_selected_action': [a.pk, b.pk], 'post': 'yes'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(GalleryItem.objects.count(), 0)
        self.assertFalse(any(os.path.exists(p) for p in paths_a + paths_b))


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

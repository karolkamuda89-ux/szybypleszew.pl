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

    def test_home_shows_visee_promo_from_migration(self):
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, 'id="nowosc"')
        self.assertContains(response, '<h2>Pióra wycieraczek VISEE</h2>')


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


class PromoSectionTests(TestCase):
    """Sekcja "Nowość": tresc z bazy, chowanie, przycisk i ograniczenia w panelu."""

    def setUp(self):
        from .models import PromoSection
        self.promo = PromoSection.objects.get()  # utworzona przez migracje 0003

    def test_edited_content_is_shown(self):
        self.promo.title = 'Nowe dywaniki'
        self.promo.bullets = 'Pierwsza zaleta\n\nDruga zaleta'  # pusta linia ma zostac pominieta
        self.promo.save()
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, 'Nowe dywaniki')
        self.assertContains(response, '<li>Pierwsza zaleta</li><li>Druga zaleta</li>')

    def test_hidden_section_is_not_rendered(self):
        self.promo.is_published = False
        self.promo.save()
        self.assertNotContains(self.client.get(reverse('core:home')), 'id="nowosc"')

    def test_button_calls_by_default_and_uses_custom_link(self):
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, 'Zapytaj o pióra: 607 560 682')
        self.promo.button_link = 'https://visee.pl'
        self.promo.save()
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, 'href="https://visee.pl" class="btn btn-cta btn-lg" target="_blank"')

    def test_admin_opens_form_and_blocks_add_and_delete(self):
        from django.contrib.auth.models import User
        self.client.force_login(User.objects.create_superuser('admin', 'admin@example.com', 'haslo-testowe'))
        response = self.client.get('/admin/core/promosection/')
        self.assertRedirects(response, f'/admin/core/promosection/{self.promo.pk}/change/')
        self.assertEqual(self.client.get('/admin/core/promosection/add/').status_code, 403)
        self.assertEqual(self.client.get(f'/admin/core/promosection/{self.promo.pk}/delete/').status_code, 403)


class ContactFormTests(TestCase):
    """Formularz kontaktowy: zapis wiadomosci, e-mail, bledy, ochrona przed spamem i panel."""

    def setUp(self):
        import time
        from django.core.cache import cache
        from .forms import make_started_token
        cache.clear()  # limit wysylek z poprzedniego testu nie moze blokowac kolejnego
        # Formularz "otwarty" 10 sekund temu – jak u czlowieka
        self.VALID = {'name': 'Jan', 'phone': '600 100 200', 'email': 'jan@example.com',
                      'car': 'Skoda Octavia 2018', 'message': 'Pęknięta szyba czołowa', 'consent': 'on',
                      'website': '', 'started': make_started_token(time.time() - 10)}

    def test_valid_message_is_saved_and_emailed(self):
        from django.core import mail
        from .models import ContactMessage
        response = self.client.post(reverse('core:home'), self.VALID)
        self.assertRedirects(response, '/#kontakt', fetch_redirect_response=False)
        msg = ContactMessage.objects.get()
        self.assertEqual(msg.phone, '600 100 200')
        self.assertTrue(msg.email_sent)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('600 100 200', mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, ['szybypleszew@interia.pl'])
        self.assertEqual(mail.outbox[0].reply_to, ['jan@example.com'])  # "Odpowiedz" -> klient
        # komunikat o wyslaniu po przekierowaniu
        self.assertContains(self.client.get(reverse('core:home')), 'Wiadomość została wysłana')

    def test_errors_are_shown_and_nothing_saved(self):
        from .models import ContactMessage
        data = dict(self.VALID, name='', phone='123', consent='')
        response = self.client.post(reverse('core:home'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Podaj imię.')
        self.assertContains(response, 'co najmniej 9 cyfr')
        self.assertContains(response, 'Zaznacz zgodę')
        self.assertFalse(ContactMessage.objects.exists())

    def test_honeypot_blocks_bots(self):
        from django.core import mail
        from .models import ContactMessage
        response = self.client.post(reverse('core:home'), dict(self.VALID, website='http://spam.example'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ContactMessage.objects.exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_too_fast_submission_is_treated_as_bot(self):
        import time
        from .forms import make_started_token
        from .models import ContactMessage
        data = dict(self.VALID, started=make_started_token(time.time() - 1))  # 1 s – za szybko na czlowieka
        response = self.client.post(reverse('core:home'), data)
        self.assertEqual(response.status_code, 302)        # bot widzi "wyslano"...
        self.assertFalse(ContactMessage.objects.exists())   # ...ale nic sie nie zapisuje

    def test_missing_or_forged_token_is_treated_as_bot(self):
        from .models import ContactMessage
        for token in ['', 'podrobiony:znacznik']:
            self.client.post(reverse('core:home'), dict(self.VALID, started=token))
        self.assertFalse(ContactMessage.objects.exists())

    def test_expired_token_asks_to_resend_and_keeps_data(self):
        import time
        from .forms import MAX_AGE, make_started_token
        from .models import ContactMessage
        data = dict(self.VALID, started=make_started_token(time.time() - MAX_AGE - 60))
        response = self.client.post(reverse('core:home'), data)
        self.assertContains(response, 'Formularz był otwarty bardzo długo')
        self.assertContains(response, 'value="Skoda Octavia 2018"')  # wpisane dane nie przepadaja
        self.assertFalse(ContactMessage.objects.exists())

    def test_rate_limit_per_ip(self):
        from .models import ContactMessage
        from .views import RATE_LIMIT_COUNT
        for _ in range(RATE_LIMIT_COUNT):
            self.client.post(reverse('core:home'), self.VALID, REMOTE_ADDR='10.0.0.1')
        response = self.client.post(reverse('core:home'), self.VALID, REMOTE_ADDR='10.0.0.1')
        self.assertContains(response, 'wysłano już kilka wiadomości')
        self.assertEqual(ContactMessage.objects.count(), RATE_LIMIT_COUNT)
        # inny adres IP nie jest blokowany
        self.client.post(reverse('core:home'), self.VALID, REMOTE_ADDR='10.0.0.2')
        self.assertEqual(ContactMessage.objects.count(), RATE_LIMIT_COUNT + 1)

    def test_client_ip_uses_last_forwarded_address(self):
        from django.test import RequestFactory
        from .views import client_ip
        # odwiedzajacy podrobil pierwszy wpis, nginx dopisal prawdziwy adres na koncu
        request = RequestFactory().get('/', HTTP_X_FORWARDED_FOR='1.2.3.4, 83.10.20.30')
        self.assertEqual(client_ip(request), '83.10.20.30')

    def test_failed_email_still_saves_message(self):
        from .models import ContactMessage
        with mock.patch('core.views.EmailMessage.send', side_effect=OSError('SMTP down')):
            self.client.post(reverse('core:home'), self.VALID)
        msg = ContactMessage.objects.get()
        self.assertFalse(msg.email_sent)

    def test_admin_lists_and_marks_read_on_open(self):
        from django.contrib.auth.models import User
        from .models import ContactMessage
        self.client.post(reverse('core:home'), self.VALID)
        msg = ContactMessage.objects.get()
        self.client.force_login(User.objects.create_superuser('admin', 'admin@example.com', 'haslo-testowe'))
        self.assertContains(self.client.get('/admin/core/contactmessage/'), 'Skoda Octavia 2018')
        self.assertEqual(self.client.get(f'/admin/core/contactmessage/{msg.pk}/change/').status_code, 200)
        msg.refresh_from_db()
        self.assertTrue(msg.is_read)
        self.assertEqual(self.client.get('/admin/core/contactmessage/add/').status_code, 403)


class FooterAndPrivacyTests(TestCase):
    """Stopka (Facebook, autor, polityka prywatnosci) i strona polityki prywatnosci."""

    def test_footer_has_social_links_author_and_privacy(self):
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, 'href="https://www.facebook.com/szybypleszew"')
        self.assertContains(response, 'Projekt i wykonanie: Karol Kamuda')
        self.assertContains(response, f'href="{reverse("core:privacy")}"')

    def test_privacy_page(self):
        response = self.client.get(reverse('core:privacy'))
        self.assertContains(response, 'Polityka prywatności')
        self.assertContains(response, 'P.H.U. AUTO MAKSYM Joanna Płukarz')


class SeoTests(TestCase):
    """SEO: mapa strony, robots.txt, tytuly i opisy, adres kanoniczny, Open Graph, dane strukturalne, 404."""

    def test_sitemap_lists_pages_and_only_live_posts(self):
        from datetime import timedelta
        from django.utils import timezone
        from .models import Post
        Post.objects.create(title='Szkic SEO', excerpt='x', content='x', is_published=False)
        Post.objects.create(title='Przyszly SEO', excerpt='x', content='x', published_at=timezone.now() + timedelta(days=5))
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        xml = response.content.decode()
        self.assertIn('<loc>http://testserver/</loc>', xml)
        self.assertIn('/blog/odprysk-na-szybie-naprawic-czy-wymienic/', xml)  # wpis z migracji startowej
        self.assertIn('/polityka-prywatnosci/', xml)
        self.assertNotIn('szkic-seo', xml)
        self.assertNotIn('przyszly-seo', xml)

    def test_robots_txt(self):
        response = self.client.get('/robots.txt')
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')
        self.assertContains(response, 'Disallow: /admin/')
        self.assertContains(response, 'Sitemap: http://testserver/sitemap.xml')

    def test_home_meta_tags(self):
        response = self.client.get(reverse('core:home') + '?utm_source=facebook')
        self.assertContains(response, '<title>Auto Szyby Pleszew – wymiana szyb samochodowych i naprawa odprysków</title>')
        self.assertContains(response, '<link rel="canonical" href="http://testserver/">')  # bez parametrow z adresu
        self.assertContains(response, 'property="og:image" content="http://testserver/static/img/og-image.jpg"')
        self.assertContains(response, '"geo": {"@type": "GeoCoordinates"')
        self.assertContains(response, 'w&nbsp;Pleszewie</span></h1>')

    def test_structured_data_is_valid_json(self):
        import json
        import re
        for url in [reverse('core:home'), '/blog/odprysk-na-szybie-naprawic-czy-wymienic/']:
            html = self.client.get(url).content.decode()
            blocks = re.findall(r'<script type="application/ld[+]json">(.*?)</script>', html, re.S)
            self.assertTrue(blocks, url)
            for block in blocks:
                json.loads(block)  # rzuci wyjatek przy blednym JSON-ie

    def test_post_has_article_meta_and_breadcrumbs(self):
        response = self.client.get('/blog/odprysk-na-szybie-naprawic-czy-wymienic/')
        self.assertContains(response, '<meta property="og:type" content="article">')
        self.assertContains(response, '"@type": "BreadcrumbList"')
        self.assertContains(response, '| Auto Szyby Pleszew</title>')

    def test_favicon_redirect(self):
        response = self.client.get('/favicon.ico')
        self.assertRedirects(response, '/static/img/favicon/favicon.ico', status_code=301, fetch_redirect_response=False)

    def test_no_template_comments_leak_into_html(self):
        # {# ... #} dziala tylko w jednej linii – rozpisany na kilka linii trafilby na strone jako tekst
        for url in [reverse('core:home'), reverse('core:blog'), reverse('core:privacy'),
                    '/blog/odprysk-na-szybie-naprawic-czy-wymienic/']:
            html = self.client.get(url).content.decode()
            self.assertNotIn('{#', html, url)
            self.assertNotIn('#}', html, url)
            self.assertNotIn('{%', html, url)

    def test_404_page_is_styled_and_noindex(self):
        response = self.client.get('/nie-ma-takiej-strony/')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'Nie ma takiej strony', status_code=404)
        self.assertContains(response, '<meta name="robots" content="noindex">', status_code=404)
        # przekierowanie na strone glowna: odliczanie w JS + zapasowy meta refresh bez JS
        self.assertContains(response, 'id="countdown"', status_code=404)
        self.assertContains(response, '<meta http-equiv="refresh" content="10;url=/">', status_code=404)


class BlogTests(TestCase):
    """Blog: lista, pojedynczy wpis, szkice/planowanie, formatowanie tresci i panel."""

    def setUp(self):
        import tempfile
        from .models import Post
        self.media = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media)
        self.override.enable()
        Post.objects.all().delete()  # startowe wpisy z migracji nie przeszkadzaja w liczeniu

    def tearDown(self):
        import shutil
        self.override.disable()
        shutil.rmtree(self.media, ignore_errors=True)

    def make_post(self, title='Testowy wpis', **kwargs):
        from .models import Post
        data = {'excerpt': 'Krótki wstęp.', 'content': 'Treść.'}
        data.update(kwargs)
        return Post.objects.create(title=title, **data)

    def test_blog_page_returns_200_when_empty(self):
        response = self.client.get(reverse('core:blog'))
        self.assertContains(response, 'Pierwsze wpisy pojawią się już wkrótce')

    def test_list_shows_only_live_posts(self):
        from datetime import timedelta
        from django.utils import timezone
        self.make_post('Widoczny')
        self.make_post('Szkic', is_published=False)
        self.make_post('Zaplanowany', published_at=timezone.now() + timedelta(days=3))
        response = self.client.get(reverse('core:blog'))
        self.assertContains(response, 'Widoczny')
        self.assertNotContains(response, 'Szkic')
        self.assertNotContains(response, 'Zaplanowany')

    def test_slug_is_generated_from_polish_title(self):
        post = self.make_post('Odprysk – naprawić czy wymienić? Łatwo!')
        self.assertEqual(post.slug, 'odprysk-naprawic-czy-wymienic-latwo')
        self.assertEqual(self.make_post('Odprysk – naprawić czy wymienić? Łatwo!').slug,
                         'odprysk-naprawic-czy-wymienic-latwo-2')

    def test_post_page_renders_formatted_content(self):
        content = (
            'Pierwszy akapit z **ważnym** słowem.\n\n'
            '## Śródtytuł\n\n'
            '- punkt jeden\n- punkt dwa\n\n'
            '[Link](https://example.com)'
        )
        post = self.make_post('Zima', content=content)
        response = self.client.get(post.get_absolute_url())
        self.assertContains(response, '<p>Pierwszy akapit z <strong>ważnym</strong> słowem.</p>')
        self.assertContains(response, '<h2>Śródtytuł</h2>')
        self.assertContains(response, '<ul><li>punkt jeden</li><li>punkt dwa</li></ul>')
        self.assertContains(response, '<a href="https://example.com" target="_blank" rel="noopener">Link</a>')

    def test_html_in_content_is_escaped(self):
        post = self.make_post('XSS', content='<script>alert(1)</script> [zly](javascript:alert(1))')
        response = self.client.get(post.get_absolute_url())
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertNotContains(response, 'href="javascript:')

    def test_draft_is_404_for_visitors_but_previewable_by_admin(self):
        from django.contrib.auth.models import User
        post = self.make_post('Szkic', is_published=False)
        self.assertEqual(self.client.get(post.get_absolute_url()).status_code, 404)
        self.client.force_login(User.objects.create_superuser('admin', 'admin@example.com', 'haslo-testowe'))
        self.assertContains(self.client.get(post.get_absolute_url()), 'Podgląd: ten wpis nie jest jeszcze widoczny')

    def test_cover_is_converted_and_files_removed_on_delete(self):
        import os
        post = self.make_post('Ze zdjęciem', cover=make_image('okladka.jpg'))
        self.assertTrue(post.cover.name.endswith('.webp'))
        self.assertTrue(post.cover_thumbnail.name.startswith('blog/min/'))
        paths = [post.cover.path, post.cover_thumbnail.path]
        post.delete()
        self.assertFalse(any(os.path.exists(p) for p in paths))

    def test_pagination(self):
        for i in range(11):
            self.make_post(f'Wpis {i}')
        response = self.client.get(reverse('core:blog'))
        self.assertContains(response, 'class="post-link"', count=9)
        self.assertContains(response, 'Strona 1 z 2')
        self.assertContains(self.client.get(reverse('core:blog') + '?strona=2'), 'class="post-link"', count=2)

    def test_admin_can_add_post(self):
        from django.contrib.auth.models import User
        from django.utils import timezone
        from .models import Post
        self.client.force_login(User.objects.create_superuser('admin', 'admin@example.com', 'haslo-testowe'))
        self.assertEqual(self.client.get('/admin/core/post/').status_code, 200)
        now = timezone.localtime()
        response = self.client.post('/admin/core/post/add/', {
            'title': 'Nowy wpis z panelu', 'slug': 'nowy-wpis-z-panelu', 'excerpt': 'Wstęp',
            'content': 'Treść wpisu', 'cover': make_image('foto.jpg'), 'cover_alt': 'Opis',
            'is_published': 'on',
            'published_at_0': now.strftime('%Y-%m-%d'), 'published_at_1': now.strftime('%H:%M:%S'),
        })
        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(slug='nowy-wpis-z-panelu')
        self.assertContains(self.client.get(post.get_absolute_url()), 'Nowy wpis z panelu')



class GoogleReviewsTests(TestCase):
    """Pobieranie opinii Google: dane zapasowe, filtrowanie, cache i obsluga bledow."""

    def setUp(self):
        # Czyscimy cache, zeby wynik jednego testu nie wplywal na kolejny
        cache.clear()

    @override_settings(GOOGLE_PLACES_API_KEY='', GOOGLE_PLACE_ID='')
    def test_without_api_key_uses_fallback(self):
        from django.conf import settings
        data = get_google_reviews()
        self.assertEqual(data['rating'], settings.GOOGLE_RATING_FALLBACK)
        self.assertEqual(data['count'], settings.GOOGLE_RATING_COUNT_FALLBACK)
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
        from django.conf import settings
        with mock.patch('core.google_reviews._fetch', side_effect=urllib.error.URLError('down')):
            data = get_google_reviews()
        self.assertEqual(data['rating'], settings.GOOGLE_RATING_FALLBACK)
        self.assertEqual(data['reviews'], [])

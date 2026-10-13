"""Modele bazy danych: galeria realizacji edytowana w panelu admina.

Jedna realizacja (GalleryItem) = jeden kafelek w galerii, np. "Mercedes G – wymiana szyby".
Realizacja moze miec kilka zdjec (GalleryPhoto) pokazujacych kolejne etapy pracy –
na stronie przewija sie je strzalkami na kafelku.
"""
from pathlib import Path

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from .images import DUZE, MINIATURA, to_webp


class GalleryItem(models.Model):
    """Realizacja w galerii (jeden kafelek)."""

    SHAPE_LANDSCAPE = 'poziome'
    SHAPE_PORTRAIT = 'pionowe'
    SHAPE_WIDE = 'szerokie'
    SHAPE_CHOICES = [
        (SHAPE_LANDSCAPE, 'Zwykły (1 × 1)'),
        (SHAPE_PORTRAIT, 'Wysoki – na zdjęcia pionowe (1 × 2)'),
        (SHAPE_WIDE, 'Szeroki (2 × 1)'),
    ]

    title = models.CharField(
        'Opis na kafelku', max_length=150,
        help_text='Np. „Mercedes G – wymiana szyby czołowej”.')
    shape = models.CharField(
        'Rozmiar kafelka', max_length=10, choices=SHAPE_CHOICES, default=SHAPE_LANDSCAPE,
        help_text='Siatka ma 4 kolumny. Wysoki kafelek zajmuje 2 rzędy, szeroki 2 kolumny.')
    order = models.PositiveIntegerField(
        'Kolejność', default=0,
        help_text='Mniejsza liczba = wyżej w galerii. Pierwsze 12 realizacji widać od razu.')
    is_published = models.BooleanField(
        'Widoczna na stronie', default=True,
        help_text='Odznacz, żeby schować realizację bez usuwania.')
    created_at = models.DateTimeField('Dodano', auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'realizacja'
        verbose_name_plural = 'Galeria – realizacje'

    def __str__(self):
        return self.title


class GalleryPhoto(models.Model):
    """Zdjecie nalezace do realizacji. Przy zapisie zamieniane na WebP + miniatura."""

    item = models.ForeignKey(
        GalleryItem, on_delete=models.CASCADE, related_name='photos', verbose_name='Realizacja')
    image = models.ImageField(
        'Zdjęcie', upload_to='galeria/',
        help_text='Dowolny format (JPG, PNG…). Zostanie automatycznie zamienione na WebP i zmniejszone.')
    # Miniatura do kafelka – tworzona automatycznie, niewidoczna w formularzu
    thumbnail = models.ImageField('Miniatura', upload_to='galeria/min/', blank=True, editable=False)
    caption = models.CharField(
        'Opis zdjęcia', max_length=150, blank=True,
        help_text='Opcjonalnie: etap pracy, np. „Demontaż starej szyby”.')
    order = models.PositiveIntegerField('Kolejność', default=0)

    class Meta:
        ordering = ['order', 'pk']
        verbose_name = 'zdjęcie'
        verbose_name_plural = 'zdjęcia'

    def __str__(self):
        return self.caption or Path(self.image.name).name

    def save(self, *args, **kwargs):
        # Zapamietujemy stare pliki, zeby po podmianie zdjecia usunac je z dysku
        old = None
        if self.pk:
            old = GalleryPhoto.objects.filter(pk=self.pk).values('image', 'thumbnail').first()

        if self.image and not self.image._committed:
            # Nowo wgrany plik: zapisujemy go od razu jako WebP (duzy + miniatura)
            stem = slugify(Path(self.image.name).stem) or 'zdjecie'
            source = self.image.file
            full = to_webp(source, DUZE)
            thumb = to_webp(source, MINIATURA)
            self.image.save(f'{stem}.webp', full, save=False)
            self.thumbnail.save(f'{stem}.webp', thumb, save=False)
        elif self.image and not self.thumbnail:
            # Zdjecie bez miniatury (np. dodane recznie) – dorabiamy ja z duzego pliku
            with self.image.open('rb') as source:
                self.thumbnail.save(f'{Path(self.image.name).stem}.webp', to_webp(source, MINIATURA), save=False)

        super().save(*args, **kwargs)

        if old:
            for field in ('image', 'thumbnail'):
                if old[field] and old[field] != getattr(self, field).name:
                    getattr(self, field).storage.delete(old[field])


@receiver(post_delete, sender=GalleryPhoto)
def delete_photo_files(sender, instance, **kwargs):
    """Po usunieciu zdjecia w panelu kasujemy tez jego pliki z dysku."""
    for field in (instance.image, instance.thumbnail):
        if field:
            field.storage.delete(field.name)


class PromoSection(models.Model):
    """Sekcja "Nowość" na stronie glownej (obecnie: pióra wycieraczek VISEE).

    W bazie jest tylko jeden taki wpis – w panelu od razu otwiera sie jego formularz.
    """

    is_published = models.BooleanField(
        'Pokazuj sekcję na stronie', default=True,
        help_text='Odznacz, żeby schować sekcję bez kasowania treści.')
    label = models.CharField(
        'Etykieta nad tytułem', max_length=60, default='Nowość',
        help_text='Mały napis nad tytułem, np. „Nowość · pióra wycieraczek”.')
    title = models.CharField('Tytuł', max_length=150)
    text = models.TextField('Opis', help_text='Pusta linia zaczyna nowy akapit.')
    bullets = models.TextField(
        'Lista zalet', blank=True,
        help_text='Każda zaleta w osobnej linii. Na stronie pojawi się jako lista z zielonymi ptaszkami.')
    button_text = models.CharField(
        'Tekst przycisku', max_length=60, blank=True, default='Zadzwoń',
        help_text='Puste = bez przycisku. Gdy pole „Link przycisku” jest puste, przycisk dzwoni do firmy '
                  'i dopisuje numer telefonu, np. „Zapytaj o pióra: 607 560 682”.')
    button_link = models.CharField(
        'Link przycisku', max_length=200, blank=True,
        help_text='Opcjonalnie, np. https://visee.pl albo #kontakt. Puste = telefon do firmy.')
    image = models.ImageField(
        'Zdjęcie', upload_to='nowosc/', blank=True,
        help_text='Dowolny format – zostanie zamienione na WebP i zmniejszone.')
    image_alt = models.CharField(
        'Opis zdjęcia (dla Google i czytników ekranu)', max_length=150, blank=True)
    placeholder = models.CharField(
        'Napis zamiast zdjęcia', max_length=30, blank=True, default='VISEE',
        help_text='Wyświetla się na grafice zastępczej, dopóki nie ma zdjęcia.')

    class Meta:
        verbose_name = 'sekcja „Nowość”'
        verbose_name_plural = 'Sekcja „Nowość”'

    def __str__(self):
        return self.title

    @property
    def bullet_list(self):
        """Lista zalet jako lista Pythona (puste linie pomijane)."""
        return [line.strip() for line in self.bullets.splitlines() if line.strip()]

    def save(self, *args, **kwargs):
        old_image = None
        if self.pk:
            old_image = PromoSection.objects.filter(pk=self.pk).values_list('image', flat=True).first()
        if self.image and not self.image._committed:
            # Nowo wgrane zdjecie zapisujemy od razu jako WebP
            stem = slugify(Path(self.image.name).stem) or 'nowosc'
            self.image.save(f'{stem}.webp', to_webp(self.image.file, DUZE), save=False)
        super().save(*args, **kwargs)
        # Po podmianie lub usunieciu zdjecia kasujemy stary plik
        if old_image and old_image != self.image.name:
            self.image.storage.delete(old_image)


class ContactMessage(models.Model):
    """Wiadomosc wyslana formularzem kontaktowym. Zapisywana zawsze – nawet gdy e-mail nie dojdzie."""

    name = models.CharField('Imię', max_length=100)
    phone = models.CharField('Telefon', max_length=30)
    email = models.EmailField('E-mail', blank=True)
    car = models.CharField('Auto', max_length=150, blank=True, help_text='Marka, model, rocznik')
    message = models.TextField('Wiadomość', blank=True)
    created_at = models.DateTimeField('Wysłano', auto_now_add=True)
    is_read = models.BooleanField('Przeczytana', default=False)
    email_sent = models.BooleanField('Powiadomienie e-mail wysłane', default=False, editable=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'wiadomość z formularza'
        verbose_name_plural = 'Wiadomości z formularza'

    def __str__(self):
        return f'{self.name} ({self.phone}) – {self.created_at:%d.%m.%Y %H:%M}'


class Post(models.Model):
    """Wpis na blogu. Lista: /blog/, pojedynczy wpis: /blog/<slug>/ (szablon core/blog_post.html)."""

    title = models.CharField('Tytuł', max_length=200)
    slug = models.SlugField(
        'Adres wpisu', max_length=200, unique=True,
        help_text='Końcówka adresu strony, np. „odprysk-naprawic-czy-wymienic”. Uzupełnia się sama z tytułu.')
    excerpt = models.TextField(
        'Krótki wstęp', max_length=400,
        help_text='1–2 zdania widoczne na liście wpisów i w wynikach Google.')
    content = models.TextField(
        'Treść',
        help_text='Pusta linia = nowy akapit. Linia zaczynająca się od „## ” = śródtytuł, „### ” = mniejszy śródtytuł, '
                  '„- ” = punkt listy. **tekst** = pogrubienie, [tekst](https://adres) = link.')
    cover = models.ImageField(
        'Zdjęcie główne', upload_to='blog/', blank=True,
        help_text='Dowolny format – zostanie zamienione na WebP i zmniejszone.')
    cover_thumbnail = models.ImageField('Miniatura', upload_to='blog/min/', blank=True, editable=False)
    cover_alt = models.CharField('Opis zdjęcia (dla Google i czytników ekranu)', max_length=150, blank=True)
    published_at = models.DateTimeField(
        'Data publikacji', default=timezone.now,
        help_text='Wpis z datą w przyszłości pojawi się na stronie automatycznie tego dnia.')
    is_published = models.BooleanField(
        'Opublikowany', default=True,
        help_text='Odznacz, żeby zapisać wpis jako szkic (niewidoczny dla odwiedzających).')
    created_at = models.DateTimeField('Utworzono', auto_now_add=True)
    updated_at = models.DateTimeField('Zmieniono', auto_now=True)

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'wpis'
        verbose_name_plural = 'Blog – wpisy'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # Uzywane m.in. przez przycisk "Pokaż na stronie" w panelu admina
        return reverse('core:blog_post', args=[self.slug])

    @property
    def is_live(self):
        """Czy wpis widza odwiedzajacy (opublikowany i data publikacji juz minela)."""
        return self.is_published and self.published_at <= timezone.now()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Post, self.title, self.pk)
        old = None
        if self.pk:
            old = Post.objects.filter(pk=self.pk).values('cover', 'cover_thumbnail').first()
        if self.cover and not self.cover._committed:
            # Nowo wgrane zdjecie: WebP duze (do wpisu) + miniatura (do listy wpisow)
            stem = slugify(Path(self.cover.name).stem) or 'wpis'
            source = self.cover.file
            full, thumb = to_webp(source, DUZE), to_webp(source, MINIATURA)
            self.cover.save(f'{stem}.webp', full, save=False)
            self.cover_thumbnail.save(f'{stem}.webp', thumb, save=False)
        elif not self.cover:
            self.cover_thumbnail = None
        super().save(*args, **kwargs)
        if old:
            for field in ('cover', 'cover_thumbnail'):
                current = getattr(self, field)
                if old[field] and old[field] != (current.name if current else ''):
                    current.storage.delete(old[field])


def unique_slug(model, text, pk=None):
    """Tworzy unikalny adres z tytulu: "Odprysk – naprawić?" -> "odprysk-naprawic" (-2, -3... przy powtorce)."""
    base = slugify(text.replace('ł', 'l').replace('Ł', 'L'))[:180] or 'wpis'
    slug, n = base, 2
    while model.objects.filter(slug=slug).exclude(pk=pk).exists():
        slug, n = f'{base}-{n}', n + 1
    return slug


@receiver(post_delete, sender=Post)
def delete_post_files(sender, instance, **kwargs):
    """Po usunieciu wpisu kasujemy jego zdjecia z dysku."""
    for field in (instance.cover, instance.cover_thumbnail):
        if field:
            field.storage.delete(field.name)

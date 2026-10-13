"""Modele bazy danych: galeria realizacji edytowana w panelu admina.

Jedna realizacja (GalleryItem) = jeden kafelek w galerii, np. "Mercedes G – wymiana szyby".
Realizacja moze miec kilka zdjec (GalleryPhoto) pokazujacych kolejne etapy pracy –
na stronie przewija sie je strzalkami na kafelku.
"""
from pathlib import Path

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
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

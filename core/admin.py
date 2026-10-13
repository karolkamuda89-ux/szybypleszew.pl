"""Panel administracyjny (/admin/): zarzadzanie galeria realizacji."""
from django import forms
from django.contrib import admin
from django.db.models import Max
from django.urls import reverse
from django.utils.html import format_html

from .models import GalleryItem, GalleryPhoto

# Naglowki panelu zamiast domyslnego "Administracja Django"
admin.site.site_header = 'Auto Szyby Pleszew – panel'
admin.site.site_title = 'Auto Szyby Pleszew'
admin.site.index_title = 'Zarządzanie stroną'


# --- Pole formularza do wgrania kilku zdjec naraz ---------------------------
# Standardowe pole Django przyjmuje jeden plik; ponizsze klasy (wg dokumentacji Django)
# pozwalaja zaznaczyc w oknie wyboru wiele plikow jednoczesnie.
class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    widget = MultipleImageInput

    def clean(self, data, initial=None):
        # Kazdy plik sprawdzamy osobno (czy to na pewno obraz)
        if isinstance(data, (list, tuple)):
            return [super(MultipleImageField, self).clean(d, initial) for d in data if d]
        return [super().clean(data, initial)] if data else []


class GalleryItemForm(forms.ModelForm):
    new_photos = MultipleImageField(
        label='Dodaj zdjęcia', required=False,
        help_text='Możesz zaznaczyć kilka plików naraz (Ctrl / Shift). '
                  'Zostaną dodane na końcu – kolejność i opisy ustawisz niżej po zapisaniu.')

    class Meta:
        model = GalleryItem
        fields = ['title', 'shape', 'order', 'is_published']


def preview(image_field, height=70):
    """Miniaturka zdjecia do wyswietlenia w panelu."""
    if not image_field:
        return '—'
    return format_html('<img src="{}" style="height:{}px;border-radius:6px;object-fit:cover">', image_field.url, height)


class GalleryPhotoInline(admin.TabularInline):
    """Zdjecia realizacji edytowane w tabelce pod formularzem realizacji."""
    model = GalleryPhoto
    extra = 0
    # Kolumna "Usunąć?" przy kazdym zdjeciu – zaznacz i zapisz, zeby usunac zdjecie (wraz z plikiem)
    can_delete = True
    fields = ['podglad', 'image', 'caption', 'order']
    readonly_fields = ['podglad']

    @admin.display(description='Podgląd')
    def podglad(self, obj):
        return preview(obj.thumbnail or obj.image, 90)


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    form = GalleryItemForm
    inlines = [GalleryPhotoInline]
    list_display = ['okladka', 'title', 'shape', 'liczba_zdjec', 'order', 'is_published', 'usun']
    list_display_links = ['okladka', 'title']
    # Kolejnosc i widocznosc mozna zmieniac od razu na liscie, bez wchodzenia w realizacje
    list_editable = ['order', 'is_published']
    list_filter = ['is_published', 'shape']
    search_fields = ['title', 'photos__caption']
    fieldsets = [
        (None, {'fields': ['title', 'shape', 'order', 'is_published']}),
        ('Zdjęcia', {'fields': ['new_photos'],
                     'description': 'Pierwsze zdjęcie jest okładką kafelka. Kolejne przewija się strzałkami.'}),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('photos')

    @admin.display(description='Okładka')
    def okladka(self, obj):
        first = obj.photos.all()[:1]
        return preview(first[0].thumbnail if first else None)

    @admin.display(description='Zdjęć')
    def liczba_zdjec(self, obj):
        return len(obj.photos.all())

    @admin.display(description='')
    def usun(self, obj):
        # Przycisk prowadzi do strony potwierdzenia Django ("Czy na pewno?") – nic nie znika od razu.
        # Usuniecie realizacji kasuje tez jej zdjecia razem z plikami w media/.
        url = reverse('admin:core_galleryitem_delete', args=[obj.pk])
        return format_html('<a href="{}" class="deletelink" style="white-space:nowrap">Usuń</a>', url)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Zdjecia z pola "Dodaj zdjecia" dopisujemy na koncu, co 10 (latwo potem wstawic cos pomiedzy)
        files = form.cleaned_data.get('new_photos') or []
        last = form.instance.photos.aggregate(m=Max('order'))['m'] or 0
        for i, uploaded in enumerate(files, start=1):
            GalleryPhoto.objects.create(item=form.instance, image=uploaded, order=last + i * 10)

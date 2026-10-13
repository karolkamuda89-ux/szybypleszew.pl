"""Panel administracyjny (/admin/): zarzadzanie galeria realizacji."""
from django import forms
from django.contrib import admin
from django.db.models import Max
from django.urls import reverse
from django.utils.html import format_html

from django.shortcuts import redirect

from .models import ContactMessage, GalleryItem, GalleryPhoto, Post, PromoSection

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


@admin.register(PromoSection)
class PromoSectionAdmin(admin.ModelAdmin):
    """Sekcja "Nowość" – jeden wpis, wiec zamiast listy od razu otwiera sie formularz."""
    fieldsets = [
        (None, {'fields': ['is_published']}),
        ('Treść', {'fields': ['label', 'title', 'text', 'bullets']}),
        ('Przycisk', {'fields': ['button_text', 'button_link']}),
        ('Zdjęcie', {'fields': ['podglad', 'image', 'image_alt', 'placeholder']}),
    ]
    readonly_fields = ['podglad']

    @admin.display(description='Obecne zdjęcie')
    def podglad(self, obj):
        return preview(obj.image, 160) if obj.pk else '—'

    def has_add_permission(self, request):
        # Drugiej sekcji nie da sie dodac – jest tylko jedna (startowa tworzona w migracji)
        return not PromoSection.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Zamiast usuwac, sekcje chowa sie odznaczajac "Pokazuj sekcje na stronie"
        return False

    def changelist_view(self, request, extra_context=None):
        # Klikniecie "Sekcja Nowosc" w menu panelu otwiera od razu formularz edycji
        promo = PromoSection.objects.first()
        if promo:
            return redirect('admin:core_promosection_change', promo.pk)
        return redirect('admin:core_promosection_add')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Wiadomosci z formularza kontaktowego – tylko do odczytu (poza znacznikiem "Przeczytana")."""
    list_display = ['created_at', 'name', 'telefon', 'car', 'skrot', 'is_read', 'email_sent']
    list_display_links = ['created_at', 'name']
    list_editable = ['is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'phone', 'email', 'car', 'message']
    readonly_fields = ['name', 'phone', 'email', 'car', 'message', 'created_at', 'email_sent']
    fields = ['created_at', 'name', 'phone', 'email', 'car', 'message', 'is_read', 'email_sent']
    actions = ['oznacz_przeczytane']

    @admin.display(description='Telefon')
    def telefon(self, obj):
        # Klikniecie numeru na telefonie od razu dzwoni do klienta
        return format_html('<a href="tel:{}">{}</a>', obj.phone.replace(' ', ''), obj.phone)

    @admin.display(description='Wiadomość')
    def skrot(self, obj):
        return (obj.message[:60] + '…') if len(obj.message) > 60 else obj.message

    @admin.action(description='Oznacz zaznaczone jako przeczytane')
    def oznacz_przeczytane(self, request, queryset):
        queryset.update(is_read=True)

    def has_add_permission(self, request):
        # Wiadomosci przychodza tylko z formularza na stronie
        return False

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Otwarcie wiadomosci w panelu oznacza ja jako przeczytana
        ContactMessage.objects.filter(pk=object_id, is_read=False).update(is_read=True)
        return super().change_view(request, object_id, form_url, extra_context)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Wpisy na blogu: dodawanie, edycja, szkice i planowanie publikacji."""
    list_display = ['miniatura', 'title', 'published_at', 'is_published', 'status', 'zobacz']
    list_display_links = ['miniatura', 'title']
    list_editable = ['is_published']
    list_filter = ['is_published']
    search_fields = ['title', 'excerpt', 'content']
    date_hierarchy = 'published_at'
    # Adres wpisu uzupelnia sie na zywo podczas wpisywania tytulu
    prepopulated_fields = {'slug': ['title']}
    readonly_fields = ['podglad', 'created_at', 'updated_at']
    fieldsets = [
        (None, {'fields': ['title', 'slug', 'excerpt', 'content']}),
        ('Zdjęcie główne', {'fields': ['podglad', 'cover', 'cover_alt']}),
        ('Publikacja', {'fields': ['is_published', 'published_at', 'created_at', 'updated_at']}),
    ]

    @admin.display(description='Zdjęcie')
    def miniatura(self, obj):
        return preview(obj.cover_thumbnail or obj.cover, 50)

    @admin.display(description='Obecne zdjęcie')
    def podglad(self, obj):
        return preview(obj.cover, 160) if obj.pk else '—'

    @admin.display(description='Status')
    def status(self, obj):
        if not obj.is_published:
            return 'Szkic'
        return 'Widoczny' if obj.is_live else 'Zaplanowany'

    @admin.display(description='')
    def zobacz(self, obj):
        # Podglad wpisu na stronie (admin widzi tez szkice i wpisy zaplanowane)
        return format_html('<a href="{}" target="_blank">Zobacz ↗</a>', obj.get_absolute_url())

"""Widoki strony firmowej.

Dane firmy (telefon, adres, godziny) trafiaja do kazdego szablonu automatycznie
przez context processor `core.context_processors.site_info`, wiec widoki przekazuja
tylko to, co jest potrzebne na konkretnej stronie.
"""
import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Prefetch
from django.shortcuts import redirect, render

from .forms import ContactForm
from .gallery import GALLERY_VISIBLE, PHOTO_ABOUT, PHOTO_HERO
from .google_reviews import get_google_reviews
from .models import GalleryItem, GalleryPhoto, PromoSection

logger = logging.getLogger(__name__)


def notify_by_email(msg):
    """Wysyla powiadomienie o nowej wiadomosci. Zwraca True, gdy sie udalo."""
    body = (
        f'Nowa wiadomość z formularza na stronie {settings.SITE_NAME}\n\n'
        f'Imię: {msg.name}\n'
        f'Telefon: {msg.phone}\n'
        f'E-mail: {msg.email or "—"}\n'
        f'Auto: {msg.car or "—"}\n\n'
        f'{msg.message or "(bez treści)"}\n'
    )
    try:
        send_mail(
            subject=f'Formularz: {msg.name}, tel. {msg.phone}',
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.CONTACT_RECIPIENTS,
        )
        return True
    except Exception as exc:  # np. zle haslo do skrzynki – wiadomosc i tak jest w bazie
        logger.error('Nie udalo sie wyslac powiadomienia e-mail: %s', exc)
        return False


def home(request):
    """Strona glowna: opinie Google, galeria (z panelu), sekcja "Nowość" i formularz kontaktowy."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Boty wypelniajace ukryte pole dostaja ten sam komunikat, ale nic nie zapisujemy
            if not form.is_spam():
                msg = form.save()
                msg.email_sent = notify_by_email(msg)
                msg.save(update_fields=['email_sent'])
            messages.success(request, 'Dziękujemy! Wiadomość została wysłana – odezwiemy się najszybciej, jak to możliwe.')
            # Przekierowanie po wyslaniu (wzorzec POST/redirect/GET): odswiezenie strony nie wysle formularza drugi raz
            return redirect('/#kontakt')
        # Przy bledach strona renderuje sie ponownie z komunikatami przy polach
    else:
        form = ContactForm()

    items = (GalleryItem.objects.filter(is_published=True)
             .prefetch_related(Prefetch('photos', queryset=GalleryPhoto.objects.order_by('order', 'pk'))))
    # Realizacje bez zdjec pomijamy – pusty kafelek nic by nie pokazal
    gallery = [item for item in items if item.photos.all()]
    return render(request, 'core/home.html', {
        'google': get_google_reviews(),
        # Sekcja "Nowość" (edytowana w panelu); None = schowana
        'promo': PromoSection.objects.filter(is_published=True).first(),
        'gallery': gallery,
        'gallery_visible': GALLERY_VISIBLE,
        'gallery_hidden_count': max(len(gallery) - GALLERY_VISIBLE, 0),
        'photo_hero': PHOTO_HERO,
        'photo_about': PHOTO_ABOUT,
        'contact_form': form,
    })


def blog(request):
    """Podstrona bloga (na razie z zapowiedziami wpisow)."""
    return render(request, 'core/blog.html')

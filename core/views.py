"""Widoki strony firmowej.

Dane firmy (telefon, adres, godziny) trafiaja do kazdego szablonu automatycznie
przez context processor `core.context_processors.site_info`, wiec widoki przekazuja
tylko to, co jest potrzebne na konkretnej stronie.
"""
import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ContactForm
from .gallery import GALLERY_VISIBLE, PHOTO_ABOUT, PHOTO_HERO
from .google_reviews import get_google_reviews
from .models import GalleryItem, GalleryPhoto, Post, PromoSection

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


POSTS_PER_PAGE = 9


def live_posts():
    """Wpisy widoczne dla odwiedzajacych: opublikowane i z data publikacji, ktora juz minela."""
    return Post.objects.filter(is_published=True, published_at__lte=timezone.now())


def blog(request):
    """Lista wpisow na blogu, po 9 na strone (?strona=2 itd.)."""
    page = Paginator(live_posts(), POSTS_PER_PAGE).get_page(request.GET.get('strona'))
    return render(request, 'core/blog.html', {'page': page})


def blog_post(request, slug):
    """Pojedynczy wpis. Szkice i wpisy zaplanowane widzi tylko zalogowany admin (podglad przed publikacja)."""
    post = get_object_or_404(Post, slug=slug)
    if not post.is_live and not request.user.is_staff:
        raise Http404
    # "Przeczytaj tez" – 3 najnowsze inne wpisy
    others = live_posts().exclude(pk=post.pk)[:3]
    return render(request, 'core/blog_post.html', {'post': post, 'others': others})


def privacy(request):
    """Polityka prywatnosci (tresc w szablonie core/privacy.html)."""
    return render(request, 'core/privacy.html')


def robots_txt(request):
    """/robots.txt – wszystko dla wyszukiwarek oprocz panelu admina, plus adres mapy strony."""
    lines = [
        'User-agent: *',
        'Disallow: /admin/',
        '',
        f'Sitemap: {request.build_absolute_uri("/sitemap.xml")}',
    ]
    return HttpResponse('\n'.join(lines) + '\n', content_type='text/plain; charset=utf-8')

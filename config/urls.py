"""Glowna mapa adresow URL projektu.

Kazdy adres strony trafia najpierw tutaj. Panel administracyjny Django jest pod /admin/,
a wszystkie adresy strony firmowej (strona glowna, blog) obsluguje aplikacja `core`.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core.sitemaps import sitemaps
from core.views import favicon, robots_txt

urlpatterns = [
    # Panel administracyjny Django (logowanie kontem superuzytkownika)
    path('admin/', admin.site.urls),
    # SEO: mapa strony i instrukcje dla robotow wyszukiwarek
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', robots_txt, name='robots'),
    # Przegladarki same pytaja o /favicon.ico – przekierowujemy do ikonki w static/
    path('favicon.ico', favicon),
    # Strona firmowa – adresy zdefiniowane w core/urls.py
    path('', include('core.urls')),
]

# W trybie deweloperskim Django sam serwuje pliki wgrane przez uzytkownikow (media/).
# Na serwerze produkcyjnym robi to serwer WWW (np. nginx), wiec ten blok sie nie wykona.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Podglad strony bledu 404 – lokalnie Django zamiast niej pokazuje swoja strone diagnostyczna
    from django.views.defaults import page_not_found
    urlpatterns += [path('podglad-404/', lambda request: page_not_found(request, None))]

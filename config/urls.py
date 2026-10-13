"""Glowna mapa adresow URL projektu.

Kazdy adres strony trafia najpierw tutaj. Panel administracyjny Django jest pod /admin/,
a wszystkie adresy strony firmowej (strona glowna, blog) obsluguje aplikacja `core`.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Panel administracyjny Django (logowanie kontem superuzytkownika)
    path('admin/', admin.site.urls),
    # Strona firmowa – adresy zdefiniowane w core/urls.py
    path('', include('core.urls')),
]

# W trybie deweloperskim Django sam serwuje pliki wgrane przez uzytkownikow (media/).
# Na serwerze produkcyjnym robi to serwer WWW (np. nginx), wiec ten blok sie nie wykona.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

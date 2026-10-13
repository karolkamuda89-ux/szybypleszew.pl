"""Adresy URL strony firmowej."""
from django.urls import path

from . import views

# Przestrzen nazw – w szablonach odwolujemy sie do adresow jako 'core:home', 'core:blog'
app_name = 'core'

urlpatterns = [
    # Strona glowna w stylu one page (oferta, o nas, galeria, kontakt, opinie)
    path('', views.home, name='home'),
    # Blog: lista wpisow i pojedynczy wpis (osobne szablony)
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.blog_post, name='blog_post'),
    # Polityka prywatnosci (link w stopce i przy zgodzie w formularzu)
    path('polityka-prywatnosci/', views.privacy, name='privacy'),
]

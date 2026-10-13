"""Adresy URL strony firmowej."""
from django.urls import path

from . import views

# Przestrzen nazw – w szablonach odwolujemy sie do adresow jako 'core:home', 'core:blog'
app_name = 'core'

urlpatterns = [
    # Strona glowna w stylu one page (oferta, o nas, galeria, kontakt, opinie)
    path('', views.home, name='home'),
    # Blog jako osobna podstrona
    path('blog/', views.blog, name='blog'),
]

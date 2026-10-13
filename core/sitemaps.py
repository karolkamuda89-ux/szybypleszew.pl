"""Mapa strony dla Google: /sitemap.xml

Zawiera strony stale (glowna, blog, polityka prywatnosci) i wszystkie opublikowane wpisy z bloga.
Nowe wpisy dodane w panelu pojawiaja sie w mapie automatycznie.
Adres mapy podaje sie w Google Search Console oraz w /robots.txt.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Post
from .views import live_posts


class StaticViewSitemap(Sitemap):
    # priority: waznosc strony wzgledem innych stron tej witryny (0.0–1.0), changefreq: jak czesto sie zmienia
    def items(self):
        return [('core:home', 1.0, 'weekly'), ('core:blog', 0.7, 'weekly'), ('core:privacy', 0.2, 'yearly')]

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]

    def changefreq(self, item):
        return item[2]


class PostSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        # Tylko wpisy widoczne dla odwiedzajacych (bez szkicow i zaplanowanych)
        return live_posts()

    def lastmod(self, post: Post):
        return post.updated_at


sitemaps = {'strony': StaticViewSitemap, 'blog': PostSitemap}

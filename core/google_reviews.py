"""Ocena i opinie z wizytowki Google (Places API (New)), z cache.

Bez klucza API albo przy bledzie zwraca wartosci zapasowe z ustawien i pusta liste opinii,
dzieki czemu strona zawsze sie wyrenderuje.
"""
import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_KEY = 'google_reviews'
FIELD_MASK = 'rating,userRatingCount,reviews,googleMapsUri'
MIN_RATING = 4
MAX_REVIEWS = 3


def _fallback():
    return {
        'rating': settings.GOOGLE_RATING_FALLBACK,
        'count': settings.GOOGLE_RATING_COUNT_FALLBACK,
        'reviews': [],
        'url': settings.GOOGLE_REVIEWS_URL,
    }


def _write_review_url():
    if settings.GOOGLE_PLACE_ID:
        return 'https://search.google.com/local/writereview?placeid=' + urllib.parse.quote(settings.GOOGLE_PLACE_ID)
    return settings.GOOGLE_REVIEWS_URL


def _fetch():
    url = 'https://places.googleapis.com/v1/places/{}?languageCode=pl'.format(
        urllib.parse.quote(settings.GOOGLE_PLACE_ID))
    request = urllib.request.Request(url, headers={
        'X-Goog-Api-Key': settings.GOOGLE_PLACES_API_KEY,
        'X-Goog-FieldMask': FIELD_MASK,
    })
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.load(response)


def _parse(data):
    reviews = []
    for item in data.get('reviews', []):
        text = (item.get('text') or item.get('originalText') or {}).get('text', '').strip()
        rating = item.get('rating', 0)
        if rating < MIN_RATING or not text:
            continue
        author = item.get('authorAttribution', {})
        reviews.append({
            'author': author.get('displayName', 'Klient Google'),
            'author_url': author.get('uri', ''),
            'author_photo': author.get('photoUri', ''),
            'rating': rating,
            'text': text,
            'when': item.get('relativePublishTimeDescription', ''),
        })
    return {
        'rating': data.get('rating', settings.GOOGLE_RATING_FALLBACK),
        'count': data.get('userRatingCount', settings.GOOGLE_RATING_COUNT_FALLBACK),
        'reviews': reviews[:MAX_REVIEWS],
        'url': data.get('googleMapsUri') or settings.GOOGLE_REVIEWS_URL,
    }


def get_google_reviews():
    if not (settings.GOOGLE_PLACES_API_KEY and settings.GOOGLE_PLACE_ID):
        result = _fallback()
    else:
        result = cache.get(CACHE_KEY)
        if result is None:
            try:
                result = _parse(_fetch())
                cache.set(CACHE_KEY, result, settings.GOOGLE_REVIEWS_CACHE_SECONDS)
            except (urllib.error.URLError, TimeoutError, ValueError) as exc:
                logger.warning('Nie udalo sie pobrac opinii Google: %s', exc)
                result = _fallback()
                # krotki cache, zeby przy awarii nie odpytywac Google przy kazdym wejsciu
                cache.set(CACHE_KEY, result, 10 * 60)
    result = dict(result)
    result['write_url'] = _write_review_url()
    result['stars_full'] = int(round(result['rating']))
    return result

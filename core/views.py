from django.shortcuts import render

from .google_reviews import get_google_reviews


def home(request):
    return render(request, 'core/home.html', {'google': get_google_reviews()})


def blog(request):
    return render(request, 'core/blog.html')

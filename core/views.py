from django.shortcuts import render


def home(request):
    return render(request, 'core/home.html')


def blog(request):
    return render(request, 'core/blog.html')

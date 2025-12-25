"""
Core views for the application
"""
from django.shortcuts import render
from django.http import HttpResponseForbidden


def csrf_failure(request, reason=""):
    """Custom CSRF failure view"""
    return render(request, 'errors/403_csrf.html', {
        'reason': reason
    }, status=403)


def handler404(request, exception):
    """Custom 404 error handler - redirect to home page"""
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    """Custom 500 error handler - redirect to home page"""
    return render(request, 'errors/500.html', status=500)


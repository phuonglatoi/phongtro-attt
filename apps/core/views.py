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


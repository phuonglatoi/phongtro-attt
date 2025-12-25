"""
Core middleware for handling 404 errors
"""
from django.shortcuts import redirect
from django.urls import resolve, Resolver404
from django.http import Http404


class Custom404Middleware:
    """
    Middleware to catch 404 errors and redirect to home page
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # If response is 404, redirect to home
        if response.status_code == 404:
            return redirect('rooms:home')
        
        return response

    def process_exception(self, request, exception):
        """
        Catch Http404 exceptions and redirect to home
        """
        if isinstance(exception, (Http404, Resolver404)):
            return redirect('rooms:home')
        return None


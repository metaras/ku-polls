"""Module for control the web application flow."""
from django.shortcuts import redirect


def index(request):
    """Redirect to the polls index.

    Returns:
        Index page.
    """
    return redirect('polls:index')

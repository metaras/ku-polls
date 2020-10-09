from django.shortcuts import redirect


def index(request):
    """Redirect to the polls index."""
    return redirect('polls:index')
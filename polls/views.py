"""Module for controlling the flow in the web application."""
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login

from .models import Question, Choice
from .forms import CreateUserForm


def registration_page(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was create for ' + user)
            return redirect('polls:login')

    context = {'form': form}
    return render(request, 'registration/registration.html', context)

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('polls:index')
        else:
            messages.info(request, 'Username or Password is incorrect')

    context = {}
    return render(request, 'registration/login.html', context)

def logged_out(request):
    logout(request)
    return redirect('polls:login')

class IndexView(generic.ListView):
    """The index page views."""

    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return poll period.

        Returns:
            Set of choice of question that from the past till now.
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:]


class DetailView(generic.DetailView):
    """The vote page."""

    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """Exclude any questions that aren't published yet.

        Returns:
            Set of choice of the question that user's request.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    """The result page."""

    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    """Check if question in the period count the vote.

    Args:
        request: user's request.
        question_id: id of question that user request

    Returns: Result page if the choice has check, otherwise detail page.

    """
    question = get_object_or_404(Question, pk=question_id)
    if question.can_vote():
        try:
            select_choice = question.choice_set.get(pk=request.POST['choice'])
        except (KeyError, Choice.DoesNotExist):
            return render(request, 'polls/detail.html', {'question': question,
                                                         'error_message': "You didn't select a choice."})
        else:
            select_choice.votes += 1
            select_choice.save()
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
    else:
        messages.error(request, "This poll was not in the polling period.")
        return redirect('polls:index')

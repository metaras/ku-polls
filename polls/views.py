"""Module for controlling the flow in the web application."""
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required

from .models import Question, Choice, Vote
from .forms import CreateUserForm

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)


def registration_page(request):
    """Register page work."""
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            logger.info('Register success: Register as {} at {}'.format(request.user.username,
                                                                   request.META.get('REMOTE_ADDR')))
            messages.success(request, 'Account was create for ' + user)
            return redirect('polls:login')

    logger.info('Register unsuccessful: Cannot register as {} at {}'.format(request.user.username,
                                                                request.META.get('REMOTE_ADDR')))
    context = {'form': form}
    return render(request, 'registration/registration.html', context)


def login_page(request):
    """Login page work."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            logger.info('Login success: Login as {} at {}'.format(request.user.username,
                                                                   request.META.get('REMOTE_ADDR')))

            return redirect('polls:index')
        else:
            messages.info(request, 'Username or Password is incorrect')
            logger.warning('Login unsuccessful: Cannot login as {} at {}'.format(request.POST['username'],
                                                                                 request.META.get('REMOTE_ADDR')))

    context = {}
    return render(request, 'registration/login.html', context)


def logged_out(request):
    """Log out page work."""
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

@login_required
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
            if not Vote.objects.filter(question=question, user=request.user).exists():
                vote = Vote.objects.create(question=question, user=request.user)
                vote.save()
            elif Vote.objects.filter(question=question, user=request.user).exists():
                vote = Vote.objects.get(question=question, user=request.user)
                if vote.choice == select_choice:
                    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
                else:
                    vote.choice = select_choice
                    vote.save()
                    logger.info('Vote success: Vote as {} at {}'.format(request.user.username,
                                                                          request.META.get('REMOTE_ADDR')))
                    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
            else:
                select_choice += 1
                select_choice.save()
                # Always return an HttpResponseRedirect after successfully dealing
                # with POST data. This prevents data from being posted twice if a
                # user hits the Back button.
                return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
    else:
        messages.error(request, "This poll was not in the polling period.")
        return redirect('polls:index')

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages

from .models import Question, Choice


class IndexView(generic.ListView):
    """The index page views."""

    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return poll period."""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:]


class DetailView(generic.DetailView):
    """The vote page."""

    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """Exclude any questions that aren't published yet."""
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    """The result page."""

    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    """Check if question in the period count the vote."""
    question = get_object_or_404(Question, pk=question_id)
    if question.can_vote():
        try:
            select_choice = question.choice_set.get(pk=request.POST['choice'])
        except (KeyError, Choice.DoesNotExist):
            return render(request, 'polls/detail.html', {
                'question': question,
                'error_message': "You didn't select a choice.",
            })
        else:
            select_choice.votes += 1
            select_choice.save()
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            return HttpResponseRedirect(reverse('polls:results',
                                                args=(question.id,)))
    else:
        messages.error(request, "This poll was not in the polling period.")
        return redirect('polls:index')

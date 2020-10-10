"""Module for testing each function."""
import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published date.

    The given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    end_time = timezone.now()+datetime.timedelta(days=30)
    return Question.objects.create(question_text=question_text, pub_date=time, end_date=end_time)


class QuestionIndexViewTests(TestCase):
    """Test the Question index page."""

    def test_no_questions(self):
        """If no questions exist, an appropriate message is displayed."""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """pub_date in the past question are displayed on the index page."""
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], ['<Question: Past question.>']
        )

    def test_future_question(self):
        """pub_date in the future question not displayed on the index page."""
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """Only past questions are displayed."""
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """The questions index page may display multiple questions."""
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )


class QuestionModelTests(TestCase):
    """Test the question modeland time period."""

    def test_was_published_recently_with_future_question(self):
        """Returns False for questions whose pub_date is in the future."""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time,
                                   end_date=time+datetime.timedelta(days=30))
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """Returns False for questions whose pub_date is older than 1 day."""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time, end_date=time+datetime.timedelta(days=30))
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """Returns True for questions whose pub_date is within the last day."""
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time, end_date=time+datetime.timedelta(days=30))
        self.assertIs(recent_question.was_published_recently(), True)

    def test_is_published_before_published_date(self):
        """is_published returns False if time was before the published date."""
        time = timezone.now() + datetime.timedelta(days=2)
        recent_question = Question(pub_date=time, end_date=time+datetime.timedelta(days=30))
        self.assertIs(recent_question.is_published(), False)

    def test_is_published_after_published_date(self):
        """is_published returns True if time was after the published date."""
        time = timezone.now() - datetime.timedelta(days=2)
        recent_question = Question(pub_date=time, end_date=time + datetime.timedelta(days=30))
        self.assertIs(recent_question.is_published(), True)

    def test_can_vote_before_published_date(self):
        """can_vote returns False if time was before published date."""
        time = timezone.now() + datetime.timedelta(days=2)
        recent_question = Question(pub_date=time, end_date=time + datetime.timedelta(days=30))
        self.assertIs(recent_question.can_vote(), False)

    def test_can_vote_after_published_date(self):
        """can_vote returns True if time was after published date."""
        time = timezone.now() - datetime.timedelta(days=2)
        recent_question = Question(pub_date=time, end_date=time + datetime.timedelta(days=30))
        self.assertIs(recent_question.can_vote(), True)

    def test_can_vote_after_end_date(self):
        """can_vote returns False if time was after end date."""
        time = timezone.now() + datetime.timedelta(days=-2)
        recent_question = Question(pub_date=time, end_date=time + datetime.timedelta(days=-1))
        self.assertIs(recent_question.can_vote(), False)


class QuestionDetailViewTests(TestCase):
    """Test the time period for vote."""

    def test_future_question(self):
        """If pub_date is in the future returns a 404 not found."""
        future_question = create_question(question_text='Future question.',
                                          days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """If pub_date in the past displays the question's text."""
        past_question = create_question(question_text='Past Question.',
                                        days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

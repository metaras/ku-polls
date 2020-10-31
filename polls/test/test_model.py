"""Module for test the model and published date of each question."""

import datetime

from django.test import TestCase
from django.utils import timezone

from polls.models import Question


class QuestionModelTests(TestCase):
    """Test the question model and time period."""

    def test_was_published_recently_with_future_question(self):
        """Returns False for questions whose pub_date is in the future."""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time,
                                   end_date=time + datetime.timedelta(days=30))
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """Returns False for questions whose pub_date is older than 1 day."""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time, end_date=time + datetime.timedelta(days=30))
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """Returns True for questions whose pub_date is within the last day."""
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time, end_date=time + datetime.timedelta(days=30))
        self.assertIs(recent_question.was_published_recently(), True)

    def test_is_published_before_published_date(self):
        """is_published returns False if time was before the published date."""
        time = timezone.now() + datetime.timedelta(days=2)
        recent_question = Question(pub_date=time, end_date=time + datetime.timedelta(days=30))
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

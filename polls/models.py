"""Models for create Question and choice in the database."""
import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Question(models.Model):
    """All about the question ex: published time."""

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    end_date = models.DateTimeField('ending date')

    def __str__(self):
        """Sent the question out."""
        return self.question_text

    def was_published_recently(self):
        """Check that question was published recently or not.

        Returns:
            True if in the vote period. False for otherwise.
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

    def is_published(self):
        """Check the published time.

        Returns:
            True if pub_date lest than now. Otherwise False.
        """
        now = timezone.now()
        return now >= self.pub_date

    def can_vote(self):
        """Check time period for voting.

        Returns:
            True if now in the vote period. Otherwise False.
        """
        now = timezone.now()
        return self.pub_date <= now <= self.end_date


class Choice(models.Model):
    """Choice for the question."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        """Sent the choice for vote in each question."""
        return self.choice_text

class Vote(models.Model):
    """Vote of each user on each question."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, default=1)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

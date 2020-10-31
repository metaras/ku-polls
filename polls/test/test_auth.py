"""Module for testing authentication"""
from django.contrib.auth import authenticate
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .test_detail import create_question

class AuthenticationTest(TestCase):

    def setUp(self):
        """Set up user for testing."""
        self.user = User.objects.create_user(username='Marry', email='Marry@gmail.com', password='secret')
        self.user.first_name = 'Marry'
        self.user.last_name = 'Tomson'
        self.user.save()

    def test_user_can_login(self):
        """Test is user can login."""
        user = authenticate(username='Marry', password='secret')
        self.assertFalse(user is None)
        self.assertTrue(user.is_authenticated)

    def test_not_login_cannot_vote(self):
        """Test if user not login yet cannot go in the detail page."""
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_can_view_question_and_result(self):
        """Test if user was not login can view the question and result list."""
        self.client.login(username='Marry', password='secret')
        self.assertTrue(self.user.is_authenticated)
        question = create_question(question_text='Future question.', days=0)
        url = reverse('polls:detail', args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
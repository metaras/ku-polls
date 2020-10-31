"""Module for match the path with its function."""
from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', login_required(views.DetailView.as_view(), login_url='polls:login'), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', login_required(views.vote, login_url='polls:login'), name='vote'),

    path('register/', views.registration_page, name='registration'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logged_out, name='logout'),
]

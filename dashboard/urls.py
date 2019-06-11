from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.list, name='list'),
    path('detail/<int:voting_id>', views.detail, name='detail'),
    path('genre/<str:name>', views.genre_votes, name='genre'),
]
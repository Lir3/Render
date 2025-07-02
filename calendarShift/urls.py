# calendarShift/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('calendarShift/', views.index, name='index'),  
]

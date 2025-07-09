from django.urls import path
from . import views

urlpatterns = [
    path('calendar/', views.calendar_view, name='shift_calendar'),
    path('edit/<str:date>/', views.edit_shift, name='edit_shift'),
]

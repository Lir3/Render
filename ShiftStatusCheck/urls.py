# ShiftStatusCheck/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.shift_status_list, name='view_submissions'), 
]

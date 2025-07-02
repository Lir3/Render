from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('generate_and_edit/', views.generate_and_edit, name='generate_and_edit'),
    path('shifts/', views.shift_list, name='shift_list'),
    path('weekly_submission_status/', views.weekly_submission_status, name='weekly_submission_status'),
]

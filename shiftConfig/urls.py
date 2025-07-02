from django.urls import path
from . import views

urlpatterns = [
    path('', views.config_form, name='shift_config'),
]

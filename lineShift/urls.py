from django.urls import path
from . import views  

urlpatterns = [
    path('submit_shift/', views.submit_shift, name='submit_shift'),
    path('liff/submit_shift/', views.submit_shift, name='submit_shift'),
    path('liff/submit_weekly_shift/', views.submit_weekly_shift, name='submit_weekly_shift'),
    path('liff/', views.liff_page, name='liff_page'),
    path('callback/', views.callback, name='callback'),
    path('liff/submit_shift/', views.submit_shift, name='liff_submit_shift'),
    path('weekly_shift/', views.weekly_shift_page, name='weekly_shift_page'),
    path("liff/get_contract_shift/", views.get_contract_shift, name="get_contract_shift"),
    path("liff/get_last_shift/", views.get_last_shift, name="get_last_shift"),
    path("liff/get_previous_week_shift/", views.get_previous_week_shift),
    path('liff/config/', views.get_shift_config, name='get_shift_config'),
    path('test/', views.test, name='test'),
]

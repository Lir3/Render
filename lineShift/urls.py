from django.urls import path
from . import views  

urlpatterns = [
    # 保存系
    path('submit_shift/', views.submit_shift, name='submit_shift'),
    path('liff/submit_shift/', views.submit_shift, name='liff_submit_shift'),

    # LIFF画面表示
    path('liff/', views.liff_page, name='liff_page'),
    path('weekly_shift/', views.weekly_shift_page, name='weekly_shift_page'),

    # データ取得系
    path('liff/get_contract_shift/<str:line_user_id>/', views.get_contract_shift, name='get_contract_shift'),
    path('liff/get_previous_week_shift/', views.get_previous_week_shift, name='get_previous_week_shift'),
    path('liff/config/', views.get_shift_config, name='get_shift_config'),

    # テスト
    path('test/', views.test, name='test'),

    # LINEログインコールバック
    path('callback/', views.callback, name='callback'),
]

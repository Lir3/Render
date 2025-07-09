from django.contrib import admin
from django.urls import include, path
from lineShift import views  
from createShift import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Dashboard.urls')),
    path('lineShift/', include('lineShift.urls')),
    path('shiftStatus/', include('ShiftStatusCheck.urls')),
    path('shiftConfig/', include('shiftConfig.urls')),
    path('dashboard/', include('Dashboard.urls')),
    path('createShift/', include('createShift.urls')), 
]

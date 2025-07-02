from django.contrib import admin
from django.urls import include, path
from lineShift import views  
from createShift import views
from calendarShift import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('createShift.urls')),
    path('lineShift/', include('lineShift.urls')),
    path('calendarShift/', include('calendarShift.urls')),
    path('shiftStatus/', include('ShiftStatusCheck.urls')),
    path('shiftConfig/', include('shiftConfig.urls')),
]

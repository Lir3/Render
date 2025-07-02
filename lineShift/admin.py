from django.contrib import admin
from .models import CustomUser, ContractShift, WeeklyShift

admin.site.register(CustomUser)
admin.site.register(ContractShift)
admin.site.register(WeeklyShift)
admin.site.register
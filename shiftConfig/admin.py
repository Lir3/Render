from django.contrib import admin
from .models import ShiftConfiguration

@admin.register(ShiftConfiguration)
class ShiftConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        'opening_time', 'closing_time',
        'weekday_min_staff', 'weekday_max_staff',
        'weekend_min_staff', 'weekend_max_staff',
        'shift_unit',
        'created_at'
    )
    readonly_fields = ('break_after_6h', 'break_after_8h')  # 編集不可

def has_add_permission(self, request):
        # すでに1件ある場合は追加を無効化
        return not ShiftConfiguration.objects.exists()
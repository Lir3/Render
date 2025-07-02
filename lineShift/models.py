from django.db import models
from django.db.models import JSONField

class CustomUser(models.Model):
    line_user_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ContractShift(models.Model):
    line_user_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=100)
    shift_data = models.JSONField()  # 全曜日分を1フィールドに保存

    def __str__(self):
        return f"{self.name} の契約シフト"
    
class WeeklyShift(models.Model):
    line_user_id = models.CharField(max_length=255)
    week_start_date = models.DateField()  # 対象週の月曜日など
    shift_data = models.JSONField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('line_user_id', 'week_start_date')

    def __str__(self):
        return f"{self.line_user_id}のシフト"

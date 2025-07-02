from datetime import timedelta
from django.db import models

def singleton_instance():
    return 1  # ID=1に固定

class ShiftConfiguration(models.Model):
    id = models.PositiveIntegerField(
        primary_key=True, default=singleton_instance, editable=False
    )

    # 営業時間
    opening_time = models.TimeField(verbose_name="営業開始時間")
    closing_time = models.TimeField(verbose_name="営業終了時間")

    # アイドルタイム
    idle_start = models.TimeField(verbose_name="アイドルタイム開始", null=True, blank=True)
    idle_end = models.TimeField(verbose_name="アイドルタイム終了", null=True, blank=True)

    # 最小・最大人数（平日・休日別）
    weekday_min_staff = models.PositiveIntegerField(default=1, verbose_name="平日：最小必要人数")
    weekday_max_staff = models.PositiveIntegerField(default=5, verbose_name="平日：最大同時人数")
    weekend_min_staff = models.PositiveIntegerField(default=1, verbose_name="休日：最小必要人数")
    weekend_max_staff = models.PositiveIntegerField(default=5, verbose_name="休日：最大同時人数")

    # 定休日
    closed_days = models.JSONField(default=list, blank=True, verbose_name="定休日（例：['月', '火']）")

    # 固定休憩ルール（編集不可）
    break_after_6h = models.DurationField(default=timedelta(minutes=45), editable=False, verbose_name="6時間超勤務時の休憩")
    break_after_8h = models.DurationField(default=timedelta(hours=1), editable=False, verbose_name="8時間超勤務時の休憩")

    # シフト単位
    SHIFT_UNIT_CHOICES = [
        (30, "30分単位"),
        (60, "60分単位"),
    ]
    shift_unit = models.PositiveIntegerField(choices=SHIFT_UNIT_CHOICES, default=30, verbose_name="シフト時間の最小単位")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"設定（{self.opening_time}〜{self.closing_time}）"

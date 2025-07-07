from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=50)  # 例: 一般, リーダー, マネージャー
    rank = models.IntegerField()  # 数字が大きいほど上位
    def __str__(self):
        return self.name
    
class Week(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        unique_together = ('start_date', 'end_date')
        
    def __str__(self):
        return f"{self.start_date} ～ {self.end_date}"

class Staff(models.Model):
    line_user_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    is_high_school_student = models.BooleanField(default=False)
    max_shifts_per_week = models.IntegerField(default=5)
    max_hours_per_day = models.DecimalField(default=8.0, max_digits=4, decimal_places=2)
    work_end_limit = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.name

class Shift(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    required_staff = models.IntegerField()

    # 役職ごとの必要人数
    required_roles = models.ManyToManyField(Role, through='ShiftRoleRequirement')

class ShiftRoleRequirement(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    min_required = models.IntegerField()

class ShiftPreference(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.staff.name} - {self.date} {self.start_time}-{self.end_time}"

class AssignedShift(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='assignedshift_set')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField() 

    class Meta:
        unique_together = ('shift', 'staff')  # 同じ人が同じシフトに重複登録されないようにする

    def __str__(self):
        return f"{self.staff.name} - {self.shift.date} {self.shift.start_time}-{self.shift.end_time}"

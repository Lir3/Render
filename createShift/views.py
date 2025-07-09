from django.shortcuts import render
from datetime import time, timedelta, datetime

def calendar_view(request):
    return render(request, 'CreateShift/calendar.html')

def generate_time_slots(start, end, unit):
    slots = []
    current = datetime.combine(datetime.today(), start)
    end_dt = datetime.combine(datetime.today(), end)
    while current <= end_dt:
        slots.append(current.strftime('%H:%M'))
        current += timedelta(minutes=unit)
    return slots

def edit_shift(request, date):
    # 仮データ（将来的にShiftConfigurationから取得）
    opening_time = time(9, 0)
    closing_time = time(23, 0)
    shift_unit = 30

    context = {
        "target_date": date,
        "time_slots": generate_time_slots(opening_time, closing_time, shift_unit),
        "users": [],  # 仮（データなし）
    }
    return render(request, "CreateShift/edit_shift.html", context)
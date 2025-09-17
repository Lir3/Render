from django.shortcuts import render
from datetime import time, timedelta, datetime
from lineShift.models import CustomUser, WeeklyShift, ContractShift


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
    # 📅 表示対象日
    target_date = datetime.strptime(date, "%Y-%m-%d").date()

    # 営業時間とスロット幅
    opening_time = time(9, 0)
    closing_time = time(23, 0)
    shift_unit = 30
    time_slots = generate_time_slots(opening_time, closing_time, shift_unit)

    users_data = []
    for user in CustomUser.objects.all():
        # そのユーザーの区分（ContractShiftに保存されている前提）
        contract = ContractShift.objects.filter(line_user_id=user.line_user_id).first()
        role = contract.name if contract else "-"

        # その週の WeeklyShift を取得
        weekly_shift = WeeklyShift.objects.filter(
            line_user_id=user.line_user_id,
            week_start_date__lte=target_date
        ).order_by("-week_start_date").first()

        available_slots = []
        if weekly_shift and str(target_date) in weekly_shift.shift_data:
            available_slots = weekly_shift.shift_data[str(target_date)]

        users_data.append({
            "name": user.name,
            "role": role,
            "start": available_slots[0] if available_slots else "-",
            "end": available_slots[-1] if available_slots else "-",
            "available_slots": available_slots,
            "shift_slots": []  # ← ここに確定シフトを入れる予定
        })

    context = {
        "target_date": target_date,
        "time_slots": time_slots,
        "users": users_data,
    }
    return render(request, "CreateShift/edit_shift.html", context)
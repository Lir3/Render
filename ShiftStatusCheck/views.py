from django.shortcuts import render
from lineShift.models import WeeklyShift, CustomUser
from django.utils.timezone import now
from datetime import timedelta

def shift_status_list(request):
    users = CustomUser.objects.all()

    # 「次週の月曜」の日付を取得
    today = now().date()
    next_monday = today + timedelta(days=(7 - today.weekday()))  # ← ここがポイント

    status_list = []

    for user in users:
        shift = WeeklyShift.objects.filter(
            line_user_id=user.line_user_id,
            week_start_date=next_monday
        ).first()

        status_list.append({
            'name': user.name,
            'week_start_date': next_monday,
            'submitted_at': shift.submitted_at if shift else None,
            'status': '提出済み' if shift and shift.shift_data else '未提出'
        })

    return render(request, 'ShiftStatusCheck/shift_status.html', {
        'status_list': status_list,
        'target_week': next_monday
    })

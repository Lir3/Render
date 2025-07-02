from django.shortcuts import render, redirect
from .models import Week, Staff, Shift, AssignedShift, ShiftPreference
from .services.shift_assignment import assign_shifts_for_week
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Prefetch
from lineShift.models import WeeklyShift
from datetime import date, timedelta
from django.utils import timezone

def dashboard(request):
    return render(request, 'dashboard.html')  # テンプレートが存在することを確認！

@csrf_protect
def generate_and_edit(request):
    if request.method == 'POST':
        # 今日を含む週の月曜〜日曜
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # 該当週がすでに存在しているか確認
        week = Week.objects.filter(start_date=start_of_week, end_date=end_of_week).first()
        if not week:
            week = Week.objects.create(start_date=start_of_week, end_date=end_of_week)

        # 自動割り当てを実行
        assign_shifts_for_week(week.id)

        return redirect('shift_list')

    return render(request, 'dashboard.html')


@csrf_protect
def shift_list(request):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    # 同じ週が複数ある場合に備えて1件目だけを取得
    week = Week.objects.filter(start_date=week_start, end_date=week_end).first()

    if not week:
        week = Week.objects.create(start_date=week_start, end_date=week_end)

    # 自動割り当て（必要なら）
    if not AssignedShift.objects.filter(shift__week=week).exists():
        assign_shifts_for_week(week.id)

    shifts = Shift.objects.filter(week=week).prefetch_related(
        Prefetch('assignedshift_set', queryset=AssignedShift.objects.select_related('staff'))
    ).order_by('date', 'start_time')

    staff_list = Staff.objects.all()

    return render(request, 'shift_list.html', {
        'shifts': shifts,
        'staff_list': staff_list,
    })

def view_submissions(request):
    # 希望提出の一覧取得ロジックを書く
    return render(request, 'view_submissions.html')

@staff_member_required
def weekly_submission_status(request):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # 月曜日

    all_users = WeeklyShift.objects.values_list('line_user_id', flat=True).distinct()
    submitted_users = WeeklyShift.objects.filter(week_start_date=week_start).values_list('line_user_id', flat=True)

    status_list = []
    for user in all_users:
        status_list.append({
            'line_user_id': user,
            'submitted': user in submitted_users,
        })

    return render(request, 'shift/view_submissions.html', {
        'week_start': week_start,
        'status_list': status_list
    })

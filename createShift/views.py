from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Prefetch
from datetime import date, datetime, timedelta
from .models import ShiftPreference, Week, Staff, Shift, AssignedShift
from .services.shift_assignment import assign_shifts_for_week
from lineShift.models import CustomUser, WeeklyShift

def dashboard(request):
    return render(request, 'dashboard.html')  # テンプレートが存在することを確認！

@csrf_protect
def generate_and_edit(request):
    print("generate_and_edit が呼び出された")
    if request.method == 'POST':
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # Weekの取得 or 作成
        week, _ = Week.objects.get_or_create(start_date=start_of_week, end_date=end_of_week)

        # WeeklyShift取得
        weekly_shifts = WeeklyShift.objects.filter(week_start_date=start_of_week)

        print(f"WeeklyShift 件数: {weekly_shifts.count()}")
        for weekly in weekly_shifts:
            print(f"User: {weekly.line_user_id}, ShiftData: {weekly.shift_data}")
            # CustomUser と Staff の対応付け
            custom_user = CustomUser.objects.filter(line_user_id=weekly.line_user_id).first()
            if not custom_user:
                print(f"CustomUser が見つかりません: {weekly.line_user_id}")
                continue
            staff = Staff.objects.filter(line_user_id=custom_user.line_user_id).first()
            if not staff:
                print(f"Staff が見つかりません: {custom_user.name}")
                continue

            for day_data in weekly.shift_data:
                print(f"{staff.name} の希望: {day_data}")
                if day_data.get("unavailable"):
                    continue

                date_str = day_data.get("date")  # 例: "07/07"
                start_str = day_data.get("start_time")
                end_str = day_data.get("end_time")

                if not (date_str and start_str and end_str):
                    continue

                try:
                    # 年を補完（今年）
                    shift_date = datetime.strptime(f"{today.year}/{date_str}", "%Y/%m/%d").date()
                    start_time = datetime.strptime(start_str, "%H:%M").time()
                    end_time = datetime.strptime(end_str, "%H:%M").time()
                except ValueError as e:
                    print(f"日付変換エラー: {e} → スキップされました。date={date_str}, start={start_str}, end={end_str}")
                    continue  # 不正なフォーマットはスキップ

                # Shiftを取得 or 作成
                shift, created = Shift.objects.get_or_create(
                    week=week,
                    date=shift_date,
                    start_time=start_time,
                    end_time=end_time
                )
                if created:
                    print(f"Shift 作成: {shift.date} {shift.start_time}-{shift.end_time}")


                # ShiftPreferenceも保存（希望として）
                ShiftPreference.objects.get_or_create(
                    staff=staff,
                    shift=shift
                )

        # 自動割り当て
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

    print(f"取得したシフト数: {shifts.count()}")
    print(f"スタッフ数: {staff_list.count()}")

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

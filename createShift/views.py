from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Prefetch, Q
from datetime import date, datetime, timedelta
from .models import ShiftPreference, Week, Staff, Shift, AssignedShift
from .services.shift_assignment import assign_shifts_for_week
from lineShift.models import CustomUser, WeeklyShift
from createShift.models import Role  # 追加：デフォルトの役職を使う場合

def dashboard(request):
    return render(request, 'dashboard.html')

@csrf_protect
def generate_and_edit(request):
    print("generate_and_edit が呼び出された")

    if request.method == 'POST':
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        week, _ = Week.objects.get_or_create(start_date=start_of_week, end_date=end_of_week)
        weekly_shifts = WeeklyShift.objects.filter(week_start_date=start_of_week)

        print(f"WeeklyShift 件数: {weekly_shifts.count()}")

        for weekly in weekly_shifts:
            print(f"User: {weekly.line_user_id}, ShiftData: {weekly.shift_data}")

            # CustomUser → Staff の関連
            custom_user = CustomUser.objects.filter(line_user_id=weekly.line_user_id).first()
            if not custom_user:
                print(f"CustomUser が見つかりません: {weekly.line_user_id}")
                continue

            staff = Staff.objects.filter(line_user_id=custom_user.line_user_id).first()
            if not staff:
                print(f"Staff が見つかりません: {custom_user.name}")
                default_role = Role.objects.filter(name="一般").first()
                staff = Staff.objects.create(
                    line_user_id=custom_user.line_user_id,
                    name=custom_user.name,
                    role=default_role
                )
                print(f"Staff を自動作成: {staff.name}")

            for day_data in weekly.shift_data:
                if day_data.get("unavailable"):
                    continue

                date_str = day_data.get("date")
                start_str = day_data.get("start_time")
                end_str = day_data.get("end_time")

                if not (date_str and start_str and end_str):
                    continue

                try:
                    shift_date = datetime.strptime(f"{today.year}/{date_str}", "%Y/%m/%d").date()
                    start_time = datetime.strptime(start_str, "%H:%M").time()
                    end_time = datetime.strptime(end_str, "%H:%M").time()
                except ValueError as e:
                    print(f"日付変換エラー: {e}")
                    continue

                # 希望者数を数えて required_staff を動的に設定
                existing_pref_count = ShiftPreference.objects.filter(
                    Q(shift__week=week) &
                    Q(date=shift_date) &
                    Q(start_time=start_time) &
                    Q(end_time=end_time)
                ).count()

                required_staff = max(existing_pref_count + 1, 1)  # 自分含む

                # Shift 作成または取得
                shift, created = Shift.objects.get_or_create(
                    week=week,
                    date=shift_date,
                    start_time=start_time,
                    end_time=end_time,
                    defaults={"required_staff": required_staff}
                )

                if created:
                    print(f"Shift 作成: {shift.date} {shift.start_time}-{shift.end_time}, required: {required_staff}")

                # ShiftPreference 登録
                ShiftPreference.objects.get_or_create(
                    staff=staff,
                    shift=shift,
                    defaults={
                        "date": shift_date,
                        "start_time": start_time,
                        "end_time": end_time
                    }
                )

        # 自動割当
        assign_shifts_for_week(week.id)

        return redirect('shift_list')

    return render(request, 'dashboard.html')


@csrf_protect
def shift_list(request):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    week = Week.objects.filter(start_date=week_start, end_date=week_end).first()
    if not week:
        week = Week.objects.create(start_date=week_start, end_date=week_end)

    # 必要なら再割当
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
    return render(request, 'view_submissions.html')


from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def weekly_submission_status(request):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

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
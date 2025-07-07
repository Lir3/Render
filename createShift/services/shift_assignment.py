from collections import defaultdict, Counter
from django.utils.dateparse import parse_time
from datetime import datetime
from lineShift.models import WeeklyShift
from createShift.models import Shift, ShiftPreference, AssignedShift, ShiftRoleRequirement, Staff, Week

def assign_shifts_for_week(week_id):
    week = Week.objects.get(id=week_id)

    # ========== 1. WeeklyShift から Shift・ShiftPreference を作成 ==========
    weekly_submissions = WeeklyShift.objects.filter(week_start_date=week.start_date)

    for submission in weekly_submissions:
        try:
            staff = Staff.objects.get(line_user_id=submission.line_user_id)
        except Staff.DoesNotExist:
            continue  # Staff 不明ならスキップ

        for day_info in submission.shift_data:
            if day_info.get('unavailable'):
                continue  # 希望なし

            date_str = day_info.get('date')
            if not date_str:
                continue

            try:
                date_obj = datetime.strptime(f"{week.start_date.year}/{date_str}", "%Y/%m/%d").date()
            except ValueError:
                continue

            start_time = parse_time(day_info.get('start_time'))
            end_time = parse_time(day_info.get('end_time'))
            if not start_time or not end_time:
                continue

            # Shift を作成（重複回避）
            shift, _ = Shift.objects.get_or_create(
                date=date_obj,
                start_time=start_time,
                end_time=end_time,
                week=week
            )

            # 仮で役職要件も作成（本番では設定画面で設定が理想）
            if not shift.required_roles.exists() and staff.role:
                ShiftRoleRequirement.objects.get_or_create(
                    shift=shift,
                    role=staff.role,
                    defaults={"min_required": 1}
                )

            # ShiftPreference を登録（重複チェックあり）
            ShiftPreference.objects.get_or_create(
                staff=staff,
                shift=shift,
                defaults={
                    "date": date_obj,
                    "start_time": start_time,
                    "end_time": end_time
                }
            )

    # ========== 2. 割り当て処理 ==========
    shifts = Shift.objects.filter(week_id=week_id).prefetch_related('required_roles')
    preferences = ShiftPreference.objects.filter(date__range=(week.start_date, week.end_date)).select_related('staff', 'shift')

    shift_pref_counts = Counter((p.shift.date, p.shift.start_time, p.shift.end_time) for p in preferences)
    sorted_shifts = sorted(shifts, key=lambda s: shift_pref_counts.get((s.date, s.start_time, s.end_time), 0))

    staff_assignments = defaultdict(list)  # staff_id → List[Shift]

    for shift in sorted_shifts:
        assigned_staff = []
        role_requirements = ShiftRoleRequirement.objects.filter(shift=shift).select_related('role').order_by('-role__rank')

        for req in role_requirements:
            role = req.role
            min_required = req.min_required

            eligible_prefs = [
                p for p in preferences
                if p.shift == shift
                and p.staff.role and p.staff.role.rank >= role.rank
                and not violates_restriction(p.staff, shift, staff_assignments)
                and p.staff not in assigned_staff
            ]

            for pref in eligible_prefs:
                if len([s for s in assigned_staff if s.role.rank >= role.rank]) >= min_required:
                    break
                if not AssignedShift.objects.filter(shift=shift, staff=pref.staff).exists():
                    AssignedShift.objects.create(
                        staff=pref.staff,
                        shift=shift,
                        start_time=shift.start_time,
                        end_time=shift.end_time
                    )
                assigned_staff.append(pref.staff)
                staff_assignments[pref.staff.id].append(shift)


def violates_restriction(staff, shift, staff_assignments):
    same_day_shifts = [s for s in staff_assignments.get(staff.id, []) if s.date == shift.date]
    total_hours = sum(
        (s.end_time.hour + s.end_time.minute / 60) - (s.start_time.hour + s.start_time.minute / 60)
        for s in same_day_shifts
    )

    shift_hours = (shift.end_time.hour + shift.end_time.minute / 60) - (shift.start_time.hour + shift.start_time.minute / 60)

    if total_hours + shift_hours > float(staff.max_hours_per_day):
        return True

    if staff.work_end_limit and shift.end_time > staff.work_end_limit:
        return True

    return False

from collections import defaultdict, Counter
from django.db.models import Prefetch
from createShift.models import Staff, Shift, ShiftPreference, AssignedShift, ShiftRoleRequirement, Week

def assign_shifts_for_week(week_id):
    week = Week.objects.get(id=week_id)
    shifts = Shift.objects.filter(week_id=week_id).prefetch_related('required_roles')
    #preferences = ShiftPreference.objects.filter(shift__week_id=week_id).select_related('staff', 'shift')
    preferences = ShiftPreference.objects.filter(date__range=(
    week.start_date, week.end_date)).select_related('staff')

    # 希望数が少ない順に (日付, start_time, end_time) をカウントして並べる
    shift_pref_counts = Counter((p.shift.date, p.shift.start_time, p.shift.end_time) for p in preferences)
    sorted_shifts = sorted(shifts, key=lambda s: shift_pref_counts.get((s.date, s.start_time, s.end_time), 0))

    staff_assignments = defaultdict(list)  # staff_id -> List[Shift]

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
                    start_time = pref.start_time if pref.start_time else shift.start_time
                    end_time = pref.end_time if pref.end_time else shift.end_time

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

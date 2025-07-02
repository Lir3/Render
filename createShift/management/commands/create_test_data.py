from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, time

from createShift.models import Role, Staff, Week, Shift, ShiftRoleRequirement, ShiftPreference

class Command(BaseCommand):
    help = "Create test data with flexible shift times (no fixed shift slots)"

    def handle(self, *args, **kwargs):
        # 役職作成
        general = Role.objects.create(name="一般", rank=1)
        leader = Role.objects.create(name="リーダー", rank=2)
        manager = Role.objects.create(name="マネージャー", rank=3)

        # スタッフ作成（中略）
        staff_list = [
            ("浅野", general, False), ("石毛", leader, False), ("石橋", general, True), ("磯辺", manager, False),
            ("生方", general, False), ("岡田", leader, False), ("小倉", general, True), ("笠原", manager, False),
            ("片平", general, False), ("加藤", leader, False), ("川野智", general, True), ("川野元", manager, False),
            ("越川", general, False), ("地頭薗", leader, False), ("鈴木", general, True), ("高橋", manager, False),
            ("竹川", general, False), ("武田", leader, False), ("田中", general, True), ("谷口", manager, False),
            ("田谷", general, False), ("時田", leader, False), ("仲野", general, True), ("中村", manager, False),
            ("名塚", general, True), ("夏目", manager, False), ("櫃間", general, False), ("藤本", leader, False),
            ("堀越", general, True), ("堀田", manager, False), ("水野", general, False), ("峰岸", leader, False),
            ("村田", general, True), ("油布", general, False), ("末原", manager, False)
        ]

        staff_objs = []
        for name, role, is_hs in staff_list:
            staff_objs.append(Staff.objects.create(
                name=name,
                role=role,
                is_high_school_student=is_hs,
                work_end_limit=time(21, 0) if is_hs else None
            ))

        # 今週
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        week = Week.objects.create(start_date=start_of_week, end_date=end_of_week)

        # シフト（1日1枠）
        shifts = []
        for i in range(7):
            date = start_of_week + timedelta(days=i)
            shift = Shift.objects.create(
                week=week,
                date=date,
                start_time=time(9, 0),
                end_time=time(21, 0),
                required_staff=6
            )
            ShiftRoleRequirement.objects.create(shift=shift, role=general, min_required=3)
            ShiftRoleRequirement.objects.create(shift=shift, role=leader, min_required=2)
            shifts.append(shift)

        # 希望シフト登録（例：先頭の何人か）
        for shift in shifts:
            if shift.date.weekday() < 5:
                ShiftPreference.objects.create(
                    staff=staff_objs[0], shift=shift, date=shift.date,
                    start_time=time(10, 0), end_time=time(14, 0)
                )
                ShiftPreference.objects.create(
                    staff=staff_objs[1], shift=shift, date=shift.date,
                    start_time=time(13, 0), end_time=time(18, 0)
                )
                ShiftPreference.objects.create(
                    staff=staff_objs[3], shift=shift, date=shift.date,
                    start_time=time(17, 0), end_time=time(21, 0)
                )
                if shift.start_time == time(9, 0):
                    ShiftPreference.objects.create(
                        staff=staff_objs[2], shift=shift, date=shift.date,
                        start_time=time(12, 0), end_time=time(16, 0)
                    )

        self.stdout.write(self.style.SUCCESS("✅ フレキシブルな希望時間でのテストデータを作成しました。"))

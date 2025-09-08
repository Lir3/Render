import json
from datetime import datetime, timedelta, date
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ContractShift, WeeklyShift, CustomUser
from shiftConfig.models import ShiftConfiguration

# ------------------------------
# 契約シフトを保存（修正版）
# ------------------------------
@csrf_exempt
def submit_shift(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            line_user_id = data.get('line_user_id')
            shifts = data.get('shifts', [])
            user_name = data.get('name')
            week_start_str = data.get("week_start")  # Vue から送信される週開始日

            if not line_user_id or not shifts or not user_name or not week_start_str:
                return JsonResponse({'error': 'Missing data'}, status=400)

            # CustomUser 保存（存在すれば上書き）
            CustomUser.objects.update_or_create(
                line_user_id=line_user_id,
                defaults={'name': user_name}
            )

            # ContractShift 上書き保存
            ContractShift.objects.filter(line_user_id=line_user_id).delete()
            formatted_shift = {}
            for day in shifts:
                formatted_shift[day.get("name")] = {
                    "start": day.get("start_time") or None,
                    "end": day.get("end_time") or None,
                    "unavailable": day.get("unavailable", False)
                }

            ContractShift.objects.create(
                line_user_id=line_user_id,
                name=user_name,
                shift_data=formatted_shift
            )

            # WeeklyShift にも保存
            week_start_date = datetime.strptime(week_start_str, "%Y-%m-%d").date()
            WeeklyShift.objects.filter(line_user_id=line_user_id, week_start_date=week_start_date).delete()

            weekly_shift_data = []
            for day in shifts:
                weekly_shift_data.append({
                    "name": day.get("name"),
                    "start_time": day.get("start_time") or "",
                    "end_time": day.get("end_time") or "",
                    "unavailable": day.get("unavailable", False)
                })

            WeeklyShift.objects.create(
                line_user_id=line_user_id,
                week_start_date=week_start_date,
                shift_data=weekly_shift_data
            )

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid method'}, status=405)


# ------------------------------
# 前週のシフトを取得
# ------------------------------
@csrf_exempt
def get_previous_week_shift(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            line_user_id = data.get("line_user_id")
            next_week_start = datetime.strptime(data.get("next_week_start"), "%Y-%m-%d").date()
            previous_week_start = next_week_start - timedelta(days=7)

            prev_shift = WeeklyShift.objects.filter(
                line_user_id=line_user_id,
                week_start_date=previous_week_start
            ).first()

            if prev_shift:
                return JsonResponse({"shift_data": prev_shift.shift_data}, status=200)
            else:
                empty_data = [{"start_time": "", "end_time": "", "unavailable": False} for _ in range(7)]
                return JsonResponse({"shift_data": empty_data}, status=200)

        except Exception as e:
            print("エラー:", e)
            return JsonResponse({"error": "サーバーエラーが発生しました"}, status=500)

    return JsonResponse({"error": "無効なHTTPメソッドです"}, status=405)


# ------------------------------
# 契約シフト取得
# ------------------------------
def get_contract_shift(request, line_user_id):
    if not line_user_id:
        return JsonResponse({"error": "line_user_id is required"}, status=400)

    try:
        contract_shift = ContractShift.objects.get(line_user_id=line_user_id)
        return JsonResponse({"shifts": contract_shift.shift_data})
    except ContractShift.DoesNotExist:
        return JsonResponse({"shifts": []})


# ------------------------------
# その他
# ------------------------------
def get_shift_config(request):
    config = ShiftConfiguration.objects.last()
    return JsonResponse({
        "opening_time": config.opening_time.strftime("%H:%M"),
        "closing_time": config.closing_time.strftime("%H:%M"),
        "shift_unit": config.shift_unit
    })

def liff_page(request):
    return render(request, 'liff/index.html')

def weekly_shift_page(request):
    return render(request, 'liff/weekly_shift.html')

def test(request):
    return render(request, 'liff/test.html')

@csrf_exempt
def callback(request):
    return HttpResponse(status=200)

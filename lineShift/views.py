import json
from datetime import datetime, timedelta,date
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ContractShift, WeeklyShift, CustomUser
from shiftConfig.models import ShiftConfiguration

@csrf_exempt
def submit_shift(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            line_user_id = data.get('line_user_id')
            shifts = data.get('shifts', [])
            user_name = data.get('name')

            if not line_user_id or not shifts or not user_name:
                return JsonResponse({'error': 'Missing data'}, status=400)

            # CustomUser に保存（存在すれば上書き）
            CustomUser.objects.update_or_create(
                line_user_id=line_user_id,
                defaults={'name': user_name}
            )

            # ContractShift を上書き保存
            ContractShift.objects.filter(line_user_id=line_user_id).delete()

            formatted_shift = {}
            for day in shifts:
                day_name = day.get("name")
                formatted_shift[day_name] = {
                    "start": day.get("start_time") or None,
                    "end": day.get("end_time") or None,
                    "unavailable": day.get("unavailable", False)
                }

            ContractShift.objects.create(
                line_user_id=line_user_id,
                name=user_name,
                shift_data=formatted_shift
            )

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid method'}, status=405)

def parse_week_start_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        pass
    try:
        this_year = date.today().year
        return datetime.strptime(f"{this_year}/{date_str}", "%Y/%m/%d").date()
    except ValueError:
        pass
    raise ValueError(f"Unsupported date format: {date_str}")

@csrf_exempt
def submit_weekly_shift(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            line_user_id = data.get('line_user_id')
            week_start_date_str = data.get('week_start_date')  # 文字列として受け取る
            shift_data = data.get('shift_data')

            if not (line_user_id and week_start_date_str and shift_data):
                return JsonResponse({'error': 'Missing data'}, status=400)

            # ここで文字列の日付をdate型に変換
            week_start_date = parse_week_start_date(week_start_date_str)

            WeeklyShift.objects.filter(line_user_id=line_user_id, week_start_date=week_start_date).delete()

            WeeklyShift.objects.create(
                line_user_id=line_user_id,
                week_start_date=week_start_date,
                shift_data=shift_data
            )

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid method'}, status=405)



@csrf_exempt
def get_previous_week_shift(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            line_user_id = data.get("line_user_id")
            next_week_start = datetime.strptime(data.get("next_week_start"), "%Y-%m-%d").date()

            # 前の週の開始日を計算
            previous_week_start = next_week_start - timedelta(days=7)

            # 前週の WeeklyShift を取得
            prev_shift = WeeklyShift.objects.filter(
                line_user_id=line_user_id,
                week_start_date=previous_week_start
            ).first()

            if prev_shift:
                return JsonResponse({"shift_data": prev_shift.shift_data}, status=200)
            else:
                # データが存在しない場合は空データを返す（全7日空欄）
                empty_data = [
                    {"start_time": "", "end_time": "", "unavailable": False}
                    for _ in range(7)
                ]
                return JsonResponse({"shift_data": empty_data}, status=200)

        except Exception as e:
            print("エラー:", e)
            return JsonResponse({"error": "サーバーエラーが発生しました"}, status=500)

    return JsonResponse({"error": "無効なHTTPメソッドです"}, status=405)


def get_contract_shift(request):
    line_user_id = request.GET.get('line_user_id')
    if not line_user_id:
        return JsonResponse({"error": "line_user_id is required"}, status=400)

    try:
        contract_shift = ContractShift.objects.get(line_user_id=line_user_id)
        return JsonResponse({"shifts": contract_shift.shift_data})
    except ContractShift.DoesNotExist:
        return JsonResponse({"shifts": []})


def get_last_shift(request):
    line_user_id = request.GET.get("line_user_id")
    last_shifts = WeeklyShift.objects.filter(line_user_id=line_user_id).order_by("-submitted_at")[:7]
    shifts = [s.shift_data for s in last_shifts[::-1]]
    return JsonResponse({"shifts": shifts})

def get_shift_config(request):
    config = ShiftConfiguration.objects.last()  # 最新の設定を取得
    return JsonResponse({
        "opening_time": config.opening_time.strftime("%H:%M"),
        "closing_time": config.closing_time.strftime("%H:%M"),
        "shift_unit": config.shift_unit
    })

# LIFF画面の表示
def liff_page(request):
    return render(request, 'liff/index.html')

def weekly_shift_page(request):
    return render(request, 'liff/weekly_shift.html')

def test(request):
    return render(request, 'liff/test.html')

@csrf_exempt
def callback(request):
    return HttpResponse(status=200)

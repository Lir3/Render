from django import forms
from .models import ShiftConfiguration

def time_choices():
    from datetime import time
    choices = []
    for hour in range(24):
        for minute in (0, 30):
            t = time(hour, minute)
            label = t.strftime("%H:%M")
            choices.append((label, label))
    return choices

class ShiftConfigurationForm(forms.ModelForm):
    
    opening_time = forms.ChoiceField(choices=time_choices(), label="営業開始時間")
    closing_time = forms.ChoiceField(choices=time_choices(), label="営業終了時間")
    idle_start = forms.ChoiceField(choices=time_choices(), required=False, label="アイドルタイム開始")
    idle_end = forms.ChoiceField(choices=time_choices(), required=False, label="アイドルタイム終了")

    WEEKDAYS = [
        ("月", "月曜日"), ("火", "火曜日"), ("水", "水曜日"),
        ("木", "木曜日"), ("金", "金曜日"), ("土", "土曜日"), ("日", "日曜日"),
    ]
    closed_days = forms.MultipleChoiceField(
        choices=WEEKDAYS,
        widget=forms.CheckboxSelectMultiple,
        label="定休日",
        required=False
    )

    class Meta:
        model = ShiftConfiguration
        exclude = ['break_after_6h', 'break_after_8h', 'created_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        input_class = 'form-control mb-2'
        checkbox_class = 'form-check-input'

        self.fields['opening_time'].widget.attrs.update({'class': input_class})
        self.fields['closing_time'].widget.attrs.update({'class': input_class})
        self.fields['idle_start'].widget.attrs.update({'class': input_class})
        self.fields['idle_end'].widget.attrs.update({'class': input_class})
        self.fields['weekday_min_staff'].widget.attrs.update({'class': input_class})
        self.fields['weekday_max_staff'].widget.attrs.update({'class': input_class})
        self.fields['weekend_min_staff'].widget.attrs.update({'class': input_class})
        self.fields['weekend_max_staff'].widget.attrs.update({'class': input_class})
        self.fields['shift_unit'].widget.attrs.update({'class': input_class})
        self.fields['closed_days'].widget.attrs.update({'class': checkbox_class})

        if self.instance and self.instance.pk:
            for field in ['opening_time', 'closing_time', 'idle_start', 'idle_end']:
                value = getattr(self.instance, field, None)
                if value:
                    # セレクトボックスで選択状態にするために「initial」ではなく「data」に代入
                    self.fields[field].widget.attrs['data-selected'] = value.strftime('%H:%M')
                    self.initial[field] = value.strftime('%H:%M')  # ←これが有効！
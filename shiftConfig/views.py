from django.shortcuts import redirect, render
from django.urls import reverse
from .models import ShiftConfiguration
from .forms import ShiftConfigurationForm

def config_form(request):
    instance = ShiftConfiguration.objects.first()

    if request.method == 'POST':
        form = ShiftConfigurationForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()  # ← 既存インスタンスを更新
            return redirect(reverse('dashboard'))
    else:
        form = ShiftConfigurationForm(instance=instance)

    return render(request, 'shiftConfig/config_form.html', {'form': form})

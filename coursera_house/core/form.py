from django import forms
from .models import Setting


class ControllerForm(forms.Form):
    # import pdb; pdb.set_trace()
    bedroom_target_temperature = forms.IntegerField(initial=Setting.objects.filter(controller_name='bedroom_target_temperature')[0].value, min_value=16, max_value=50)
    hot_water_target_temperature = forms.IntegerField(initial=Setting.objects.filter(controller_name='hot_water_target_temperature')[0].value, min_value=16, max_value=50)
    bedroom_light = forms.BooleanField(initial=Setting.objects.filter(controller_name='bedroom_light')[0].value)
    bathroom_light = forms.BooleanField(initial=Setting.objects.filter(controller_name='bathroom_light')[0].value)

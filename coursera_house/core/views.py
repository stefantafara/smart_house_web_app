from django.urls import reverse_lazy
from django.views.generic import FormView
from django.shortcuts import render

from .models import Setting
from .form import ControllerForm
from .tasks import controller_polling
from .models import Setting


class ControllerView(FormView):
    form_class = ControllerForm
    template_name = 'core/control.html'
    success_url = reverse_lazy('form')

    def get_context_data(self, **kwargs):
        context = super(ControllerView, self).get_context_data()
        context['data'] = controller_polling()
        print(context)
        return context

    def get_initial(self):
        # import pdb; pdb.set_trace()
        return {'bedroom_target_temperature': Setting.objects.filter(controller_name='bedroom_target_temperature')[0].value,
                'hot_water_target_temperature': Setting.objects.filter(controller_name='hot_water_target_temperature')[0].value,
                'bedroom_light': True if Setting.objects.filter(controller_name='bedroom_light')[0].value == 1 else False,
                'bathroom_light': True if Setting.objects.filter(controller_name='bathroom_light')[0].value == 1 else False
                }

    def form_valid(self, form):
        # import pdb; pdb.set_trace()
        print('trying to save to database...')

        # getting objects from databases
        bedroom_target_temperature = Setting.objects.filter(controller_name='bedroom_target_temperature')[0]
        hot_water_target_temperature = Setting.objects.filter(controller_name='hot_water_target_temperature')[0]
        bedroom_light = Setting.objects.filter(controller_name='bedroom_light')[0]
        bathroom_light = Setting.objects.filter(controller_name='bathroom_light')[0]

        # saving to database
        bedroom_target_temperature.value = form.cleaned_data['bedroom_target_temperature']
        bedroom_target_temperature.save()
        hot_water_target_temperature.value = form.cleaned_data['hot_water_target_temperature']
        hot_water_target_temperature.save()
        bedroom_light.value = form.cleaned_data['bedroom_light']
        bedroom_light.save()
        bathroom_light.value = form.cleaned_data['bathroom_light']
        bathroom_light.save()
        print('Saved to database.')
        return super(ControllerView, self).form_valid(form)

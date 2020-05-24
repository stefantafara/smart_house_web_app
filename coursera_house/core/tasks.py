from __future__ import absolute_import, unicode_literals
from celery import task
import requests, logging, json
from django.conf import settings
from celery.utils.log import get_task_logger
import celery
from django.core.mail import send_mail


from .models import Setting
from django.conf import settings

TOKEN = 'dbac9fcdb2b43d5d9465e705b313ac5d1610057e10fd6a9de515249106ed37c5'
HEADERS_AUTH = {"Authorization": "Bearer dbac9fcdb2b43d5d9465e705b313ac5d1610057e10fd6a9de515249106ed37c5"}


@task()
def smart_home_manager():
    # checking if ALERT setting exists
    if len(Setting.objects.filter(controller_name='alert')) == 0:
        print('Creating alert setting in database')
        alert = Setting(controller_name='alert', label='Уведомление', value=False)
        alert.save()
    # checking if COLD_WATER setting exists
    if len(Setting.objects.filter(controller_name='cold_water')) == 0:
        print('Creating cold_water setting in database')
        cold_water = Setting(controller_name='cold_water', label='Включена холодная вода', value=False)
        cold_water.save()
    # Здесь ваш код для проверки условий
    print('polling controllers...')
    ctrl_dict = controller_polling()
    # import pdb; pdb.set_trace()

    # synchronizing bedroom_light
    value_db = Setting.objects.filter(controller_name='bedroom_light')[0].value
    value_ctrl = ctrl_dict['bedroom_light']
    if value_db != value_ctrl:
        set_controller({'bedroom_light': value_db})

    # synchronizing bedroom_light
    value_db = Setting.objects.filter(controller_name='bathroom_light')[0].value
    value_ctrl = ctrl_dict['bathroom_light']
    if value_db != value_ctrl:
        set_controller({'bathroom_light': value_db})

    # WATER LEAK
    water_leak = ctrl_dict['leak_detector']
    alert = Setting.objects.filter(controller_name='alert')[0]
    if water_leak and not alert.value:
        print('WATER LEAK!!!!!!')
        set_controller({'cold_water': False,
                        'hot_water': False})
        alert.value = True
        alert.save()
        # send_mail('Smart house Alert: WATER LEAK', 'We have turned of cold/hot water','smarthouse@smarthouse.com',EMAIL_RECEPIENT,fail_silently=False,)
    elif not water_leak and alert.value:
        alert.value = False
        alert.save()

    # COLD WATER
    # import pdb; pdb.set_trace()
    cold_water = ctrl_dict['cold_water']
    boiler = ctrl_dict['boiler']
    washing_machine = ctrl_dict['washing_machine']
    if not cold_water and (boiler or washing_machine):
        set_controller({'boiler': False,
                        'washing_machine': 'off'})



def controller_polling():
    print('polling controllers...')
    url = 'https://smarthome.webpython.graders.eldf.ru/api/user.controller'
    resp = requests.get(url, headers=HEADERS_AUTH)
    # print(f'received: {resp.text}')
    # log(f'received: {resp.text}')
    resp_dict = json.loads(resp.text)
    data = resp_dict['data']
    kv_dict = {}
    for item in data:
        kv_dict[item['name']] = item['value']
    # print(f'kv_dict = {kv_dict}')
    return kv_dict


def set_controller(controller_dict):
    print('setting value to controller {controller_name}...')
    post_dict = {'controllers': []}
    for controller in controller_dict:
        post_dict['controllers'].append({'name': controller, 'value': controller_dict[controller]})
    # import pdb;    pdb.set_trace()
    post_json = json.dumps(post_dict)
    print(f'post_dict = {post_dict}')
    post_to_controller(post_json)
    print(f'post_json = {post_json}')
    # import pdb;    pdb.set_trace()


def post_to_controller(data):
    url = 'https://smarthome.webpython.graders.eldf.ru/api/user.controller'
    resp = requests.post(url, headers=HEADERS_AUTH, data=data)
    print(f'response: {resp.text}')

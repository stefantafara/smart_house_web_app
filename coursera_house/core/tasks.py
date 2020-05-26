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
    post_dict = {}
    # import pdb; pdb.set_trace()

    # read from controllers
    water_leak = ctrl_dict['leak_detector']
    cold_water = ctrl_dict['cold_water']
    hot_water = ctrl_dict['hot_water']
    boiler = ctrl_dict['boiler']
    washing_machine = ctrl_dict['washing_machine']
    boiler_temperature = 0 if ctrl_dict['boiler_temperature'] is None else int(ctrl_dict['boiler_temperature'])
    smoke_detector = ctrl_dict['smoke_detector']
    bedroom_light = ctrl_dict['bedroom_light']
    bathroom_light = ctrl_dict['bathroom_light']
    bedroom_temperature = ctrl_dict['bedroom_temperature']
    outdoor_light = ctrl_dict['outdoor_light']
    curtains = ctrl_dict['curtains']
    air_conditioner = ctrl_dict['air_conditioner']

    # read from database
    hot_water_target_temperature = int(Setting.objects.filter(controller_name='hot_water_target_temperature')[0].value)
    bedroom_light_db = Setting.objects.filter(controller_name='bedroom_light')[0].value
    bathroom_light_db = Setting.objects.filter(controller_name='bathroom_light')[0].value
    bedroom_target_temperature = int(Setting.objects.filter(controller_name='bedroom_target_temperature')[0].value)
    bedroom_light_db_object = Setting.objects.filter(controller_name='bedroom_light')[0]
    bathroom_light_db_object = Setting.objects.filter(controller_name='bathroom_light')[0]

    # synchronizing bedroom_light
    if smoke_detector and bedroom_light_db:
        bedroom_light_db_object.value = False
        bedroom_light_db_object.save()
    if bedroom_light_db != bedroom_light and not smoke_detector:
        post_dict['bedroom_light'] = bedroom_light_db
        # set_controller({'bedroom_light': bedroom_light_db})

    # synchronizing bedroom_light
    if smoke_detector and bathroom_light_db:
        bathroom_light_db_object.value = False
        bathroom_light_db_object.save()
    if bathroom_light_db != bathroom_light and not smoke_detector:
        post_dict['bathroom_light'] = bathroom_light_db
        # set_controller({'bathroom_light': bathroom_light_db})

    # WATER LEAK
    alert = Setting.objects.filter(controller_name='alert')[0]
    if water_leak and not alert.value and (cold_water or hot_water or boiler or washing_machine == 'on'):
        print('WATER LEAK!!!!!!')
        post_dict['cold_water'] = False
        post_dict['hot_water'] = False
        post_dict['boiler'] = False
        post_dict['washing_machine'] = 'off'
        alert.value = True
        alert.save()
        send_mail('Smart house Alert: WATER LEAK', 'We have turned of cold/hot water','smarthouse@smarthouse.com',
                  [settings.EMAIL_RECEPIENT], fail_silently=False,)
    elif not water_leak and alert.value:
        alert.value = False
        alert.save()
    '''if water_leak:
        print('WATER LEAK!!!!!!')
        post_dict['cold_water'] = False
        post_dict['hot_water'] = False
        post_dict['boiler'] = False
        post_dict['washing_machine'] = 'off'
        # set_controller({'cold_water': False, 'hot_water': False, 'boiler': False, 'washing_machine': 'off'})
        send_mail('Smart house Alert: WATER LEAK', 'We have turned of cold/hot water', 'smarthouse@smarthouse.com',
                  [settings.EMAIL_RECEPIENT], fail_silently=False, )'''

    # COLD WATER
    # import pdb; pdb.set_trace()
    if not water_leak and not cold_water and (boiler or washing_machine == 'on'):
        print(f'cold_water={cold_water}  boiler={boiler}  washing_machine={washing_machine}')
        post_dict['boiler'] = False
        post_dict['washing_machine'] = 'off'
        # set_controller({'boiler': False, 'washing_machine': 'off'})

    # boiler_temperature
    if not water_leak and boiler_temperature <= 0.9 * hot_water_target_temperature and not boiler and cold_water and not smoke_detector:
        post_dict['boiler'] = True
        # set_controller({'boiler': True})
    if not water_leak and boiler_temperature >= 1.1 * hot_water_target_temperature and boiler:
        post_dict['boiler'] = False
        # set_controller({'boiler': False})

    # outdoor_light
    print(f'outdoor_light={outdoor_light}   bedroom_light={bedroom_light}   curtains={curtains}')
    if curtains != 'slightly_open':
        if outdoor_light < 50 and curtains == 'close':
            post_dict['curtains'] = 'open'
            # set_controller({'curtains': 'open'})
        elif (outdoor_light > 50 or bedroom_light) and curtains == 'open':
            post_dict['curtains'] = 'close'
            # set_controller({'curtains': 'close'})

    # smoke_detector
    print(f'smoke_detector={smoke_detector}  air_conditioner={air_conditioner}  bedroom_light={bedroom_light} '
          f'bathroom_light={bathroom_light}  boiler={boiler}  washing_machine={washing_machine}')
    if smoke_detector and (air_conditioner or bedroom_light or bathroom_light or boiler or washing_machine == 'on'):
        print('SMOKE!!!!!!!!')
        post_dict['air_conditioner'] = False
        post_dict['bedroom_light'] = False
        post_dict['bathroom_light'] = False
        post_dict['boiler'] = False
        post_dict['washing_machine'] = 'off'
        '''set_controller({'air_conditioner': False,
                        'bedroom_light': False,
                        'bathroom_light': False,
                        'boiler': False,
                        'washing_machine': 'off'}
                       )'''

    # bedroom_temperature
    if bedroom_temperature <= 0.9 * bedroom_target_temperature and air_conditioner:
        post_dict['air_conditioner'] = False
        # set_controller({'air_conditioner': False})
    if bedroom_temperature >= 1.1 * bedroom_target_temperature and not smoke_detector and not air_conditioner:
        post_dict['air_conditioner'] = True
        # set_controller({'air_conditioner': True})

    # if we should send commands to controllers
    print(f'post_dict={post_dict}')
    if post_dict != {}:
        set_controller(post_dict)


def controller_polling():
    print('polling controllers...')
    # url = 'https://smarthome.webpython.graders.eldf.ru/api/user.controller'
    url = settings.SMART_HOME_API_URL
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
    # print('setting value to controller {controller_name}...')
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
    # url = 'https://smarthome.webpython.graders.eldf.ru/api/user.controller'
    url = settings.SMART_HOME_API_URL
    resp = requests.post(url, headers=HEADERS_AUTH, data=data)
    print(f'response: {resp.text}')

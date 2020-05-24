from __future__ import absolute_import, unicode_literals
from celery import task
import requests, logging, json
from celery.utils.log import get_task_logger
import celery


from .models import Setting

TOKEN = 'dbac9fcdb2b43d5d9465e705b313ac5d1610057e10fd6a9de515249106ed37c5'
HEADERS_AUTH = {"Authorization": "Bearer dbac9fcdb2b43d5d9465e705b313ac5d1610057e10fd6a9de515249106ed37c5"}
logger = logging.getLogger('celery')

'''
@celery.signals.after_setup_logger.connect
def on_after_setup_logger(**kwargs):
    logger = logging.getLogger('celery')
    logger.propagate = True
    logger = logging.getLogger('celery.app.trace')
    logger.propagate = True'''


@task()
def smart_home_manager():
    # Здесь ваш код для проверки условий
    logger.info('polling controllers...')
    controller_polling()
    # import pdb; pdb.set_trace()


def controller_polling():
    print('polling controllers...')
    url = 'https://smarthome.webpython.graders.eldf.ru/api/user.controller'
    resp = requests.get(url, headers=HEADERS_AUTH)
    # print(f'received: {resp.text}')
    # log(f'received: {resp.text}')
    respdict = json.loads(resp.text)
    data = respdict['data']
    kv_dict = {}
    for item in data:
        kv_dict[item['name']] = item['value']
    # print(f'kv_dict = {kv_dict}')
    return kv_dict


def log(output):
    with open(r'C:\PycharmProjects\smart_house_web_app\server.log', 'w+') as file:
        file.write(output)

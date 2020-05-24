GET https://smarthome.webpython.graders.eldf.ru/api/auth.current -H 'Authorization: Bearer dbac9fcdb2b43d5d9465e705b313ac5d1610057e10fd6a9de515249106ed37c5
curl get https://smarthome.webpython.graders.eldf.ru/api/user.controller -H 'Authorization: Bearer dbac9fcdb2b43d5d9465e705b313ac5d1610057e10fd6a9de515249106ed37c5'

#######################################
          TAB 1 - DJANGO
#######################################
cd C:\PycharmProjects\smart_house_web_app\
pipenv shell
python.exe .\manage.py runserver

#######################################
          TAB 2 - CELERY - WORKER
#######################################
cd C:\PycharmProjects\smart_house_web_app\
pipenv shell
celery -A coursera_house.celery:app worker --pool=solo -l info

#######################################
          TAB 3 - CELERY - BEAT
#######################################
cd C:\PycharmProjects\smart_house_web_app\
pipenv shell
celery -A coursera_house.celery:app beat -l info

#######################################
          TAB 4 - REDIS
#######################################
Ubuntu:
sudo service redis-server start

#######################################
          TAB 5 - SQLITE
#######################################
cd C:\PycharmProjects\smart_house_web_app\
.\sqlite3.exe .\db.sqlite3
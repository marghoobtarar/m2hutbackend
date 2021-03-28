from django.apps import AppConfig
# from .scheduler import start
from dateutil.parser import parse


class AdminsideConfig(AppConfig):
    name = 'adminside'
    # print('this is admin config')
    # def ready(self):
    #     from .scheduler import notify_user
    #     notify_user(schedule=parse('2021-03-16 12:09:50.597965+00:00'))

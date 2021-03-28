from django_cron import CronJobBase, Schedule
from django.utils import timezone
class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1 # every 2 hours
    ALLOW_PARALLEL_RUNS = True
    DJANGO_CRON_CACHE = 'cron_cache'


    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'my_app.my_cron_job'    # a unique code

    def do(self):
        payload = {}
        payload['created_at'] = timezone.now()
        payload['present'] = True
       
        print('serilizer is wrong')
        # Attandance.objects.create(created_at = ,present=False)
        # pass    # do your thing here
# from django.utils import timezone

# from .models import Attandance

# def my_scheduled_job():

#     Attandance.objects.create(created_at = timezone.now(),present=False)
#     print('testing')
# #   pass
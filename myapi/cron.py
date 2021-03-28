from django_cron import CronJobBase, Schedule
from django.db.models import Q

from adminside.models import (
                                WorkLogsModel,
                                )
from adminside.serializer import (
                                    WorkLogSerilizer,
                                    )
from UserAuth.models import User
from UserAuth.serializer import UserCreateSerializer
from django.utils import timezone 
from user.views import convert_to_hours
import datetime
#  here online attandance function will be performed

def my_scheduled_job():
        payload = {}
        users = User.objects.values('id').filter(~Q(admin_id = None))
        today = timezone.datetime.today()

        for user in users:
            len_data = WorkLogsModel.objects.filter(user_id = user['id'],
                                                created_at__year = today.year,
                                                created_at__month = today.month,
                                                created_at__day = today.day
                                                )
                    
            # print('today is' , today, len(len_data))
            if len(len_data) == 0:
                # print('user today data is not exists so mark them absent by entering null data')
                payload['user_id'] = user['id']
                payload['end_at'] = timezone.now()
                serializer = WorkLogSerilizer(data = payload)
                if serializer.is_valid():
                    serializer.save()
def automatic_clockout():
    today = timezone.datetime.today()
    payload = {}
    unclocked_data = WorkLogsModel.objects.values('id','created_at','end_at').filter(~Q(user_id__admin_id = None)  ,
                                                created_at__year = today.year,
                                                created_at__month = today.month,
                                                created_at__day = today.day,
                                                # total_works_hours = None,
                                                end_at = None
                                                )
    for data in unclocked_data :
        current_time_seconds = (today.second + 
                                today.minute * 60 +
                                today.hour * 3600) 
        previous_time_seconds = ( data['created_at'].second +
                                 data['created_at'].minute * 60 +
                                 data['created_at'].hour * 3600 )
        working_hours = abs(current_time_seconds - previous_time_seconds)
        converted_time_into_hours =  convert_to_hours(working_hours)
        date = datetime.datetime.strptime(converted_time_into_hours,'%H:%M:%S')
        if(date.hour >= 10):
            payload = {}
            payload['end_at'] = today
            payload['total_works_hours'] = converted_time_into_hours
            serilizer = WorkLogSerilizer(WorkLogsModel.objects.get(
                                        id = data['id']),
                                        data = payload)
            if serilizer.is_valid():
                serilizer.save()

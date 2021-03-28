from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics
from django.db.models import Sum, Count, Avg, Q
from django.http import HttpResponse
from django.conf import settings
from operator import itemgetter
import os
from django.utils.timezone import datetime #important if using timezones
import datetime as dt
import math

import base64
from django.core.files.base import ContentFile

# from datetime import datetime, date

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
import pandas as pd
import time
# jwt decoder
from rest_framework_jwt.utils import jwt_decode_handler
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
# custom decorators
# from .decorators import authors_only, MyDecorator

# import serilizers
from adminside.serializer import CustomTokenObtainPairSerializer
# import models
from UserAuth.models import User
from adminside.models import (WorkLogsModel, 
                             WorkLogsDetailsModel,
                             WorkLogsBreakModel,
                             NoticesModel,
                             StyleModel,
                             TypographyModel)

from adminside.serializer import (WorkLogSerilizer, 
                                 WorkLogDetailsSerilizer,
                                 WorkLogsBreakSerilizer,
                                 NoticesSerializer,
                                 StyleSerializer,
                                 TypographySerializer)

class CustomTokenObtainPairView(TokenObtainPairView):
    # Replace the serializer with your custom
    serializer_class = CustomTokenObtainPairSerializer

class DashboardAnalytics(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        print('this is inside the user', )
        try:
            today = datetime.today()
            data = {}
            user = getUser(request)
            admin = User.objects.values('admin_id').get(id = user)
            notice =NoticesSerializer( NoticesModel.objects.filter(admin_id = admin['admin_id'],
                                                                publish=True).last()).data
            absents = WorkLogsModel.objects.filter(
                                        created_at__month = today.month,    
                                        created_at__year = today.year,
                                        total_works_hours = None  , 
                                         user_id = user,         
                                        ).\
                                        aggregate(Count('id'))['id__count']
            presents = WorkLogsModel.objects.filter( ~Q(total_works_hours = None ) ,
                                        created_at__month = today.month,
                                        created_at__year = today.year,
                                        user_id = user,         
                                       ).\
                                        aggregate(Count('id'))['id__count']

            total_workdays = WorkLogsModel.objects.\
                                    values('total_works_hours', 'created_at__date').\
                                        filter( ~Q(total_works_hours = None) , 
                                            created_at__month = today.month,
                                            created_at__year = today.year,
                                            user_id = user,         
                                       )    
            graph_workdays = WorkLogsModel.objects.\
                                    values('total_works_hours', 'created_at__date').\
                                        filter( ~Q(total_works_hours = None) , 
                                            # created_at__month = today.month,
                                            # created_at__year = today.year,
                                            user_id = user,         
                                       )    
            previous_seconds = 0
            loop = 0
            for dat in graph_workdays:
                graph_workdays[loop]['total_works_hours__hour'] = dat['total_works_hours'].hour + \
                                                            dat['total_works_hours'].minute/60
                graph_workdays[loop].pop('total_works_hours')
                loop+=1
            for dat in total_workdays:
                date = datetime.strptime(str( dat['total_works_hours']),'%H:%M:%S.%f')
                previous_seconds = (date.second + date.minute*60 + date.hour*3600) + previous_seconds
            data['total_work_hours'] = convert_to_hours(previous_seconds)
            data['absents'] = absents
            data['presents'] = presents 
            data['notices'] = notice
            data['working_hours'] = graph_workdays
                      
        except ValidationError as v:
            return Response({'message':'there is an error',
                            
                            'error' : v},
                            status= status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'message':'analytics data',
                            'analytics': data })

# ******************************* Work logs***********************#
class WorkLogs(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            today = datetime.today()
            data = WorkLogsModel.objects.values('id',
             'created_at', 'end_at', 
             'total_break_time',
             'total_works_hours','user_id').filter(user_id = getUser(request))

            print(data)
            i = 0

            for dat in data:
                address = WorkLogsDetailsModel.objects.values('address').filter(worklog_id = dat['id']).order_by('-created_at').first()
                print('address is',address)
                data[i]['address']  = address['address']
                i += 1
        
            return Response({'messag':'Work Log list retrieved successfully.',
                            'work_logs':
                           data},
                                status=status.HTTP_200_OK)
        except ValidationError as v:
            return Response ({'message':'This is an error is fetching logs',
                                'error':v},
                               status=status.HTTP_400_BAD_REQUEST )
    def post(self, request):
        payload = request.data
        # print('notice data', payload)
        _mutable = payload._mutable
        payload._mutable = True
        
        payload['captured_image'] = base64_file(payload['captured_image'])
        payload['end_at'] = ''
        payload._mutable = _mutable
        # image = ImageModel.objects.create()
        # print('the image is here ',image)

        # or even base64 files, with custome name
        # file = FileModel.objects.create(base64_file(data=img_base64_str, name="custome_name"))
        today = datetime.today()
        try:
            _mutable = payload._mutable
            payload._mutable = True
            payload['user_id'] = getUser(request)
            isExist = [WorkLogSerilizer(dat).data for dat in WorkLogsModel.objects.filter(created_at__year=today.year,
                                       created_at__month=today.month,
                                       created_at__day=today.day, user_id = payload['user_id'])]
            if not isExist:

                payload._mutable = _mutable
                serilizer = WorkLogSerilizer(data = payload)
                if(serilizer.is_valid()):
                    
                    serilizer.save()
                    worklog_id = serilizer.data['id']
                    _mutable = payload._mutable
                    payload._mutable = True
                    payload['worklog_id'] = serilizer.data['id']
                    payload['work_log_break_id'] = None

                    payload._mutable = _mutable
                    detail = WorkLogDetailsSerilizer(data = payload)
                    if(detail.is_valid()):
                        
                        detail.save()
                        return Response(
                        {'message':"Work log created successfully",
                        'work_log':serilizer.data,
                        'work_log_details':detail.data},
                        status = status.HTTP_201_CREATED )
                    else:
                        return Response(
                        {'message':"Work log detail serilizer is not valid",
                        'error':detail.errors
                        }
                       ,
                        status = status.HTTP_400_BAD_REQUEST )


                    # print(serilizer.data)
                    
                else:
                    
                    # if()
                    return Response(
                            {'message':"Data is not serilized form"},
                            status = status.HTTP_400_BAD_REQUEST
                            )
            else:
                if(int( payload['worklog_type'])== 2):
                    if(WorkLogsDetailsModel.objects.filter(created_at__year=today.year,
                                       created_at__month=today.month,
                                       created_at__day=today.day,
                                       worklog_id =isExist[0]['id'],
                                       worklog_type = 2).exists()):
                         return Response(
                                    {
                                        'error':"you have already clocked out",
                                    },
                                    status = status.HTTP_400_BAD_REQUEST )
                    else:
                        payload['end_at'] = datetime.today() 
                        created_at = isExist[0]['created_at']
                        payload['worklog_id'] = isExist[0]['id']
                        payload['work_log_break_id'] = None
                        payload['total_works_hours']= str(datetime.today() - getHours(created_at))
                        payload._mutable = _mutable
                        update_worklog = WorkLogSerilizer( WorkLogsModel.objects.get(id = isExist[0]['id']),data = payload)
                        if(update_worklog.is_valid()):
                            update_worklog.save()
                            serializer = WorkLogDetailsSerilizer( data = payload )
                            if serializer.is_valid():
                                serializer.save()
                                return Response(
                                    {'message':"Work log break out successfully",
                                    'work_log':update_worklog.data,
                                    'work_log_details': serializer.data},
                                    status = status.HTTP_201_CREATED )
                        else:
                            return Response(
                                {'message':"Data is not serilized form"},
                                status = status.HTTP_400_BAD_REQUEST
                                )
                elif(int( payload['worklog_type'])== 3 ):
                    if(WorkLogsDetailsModel.objects.filter(created_at__year=today.year,
                                       created_at__month=today.month,
                                       created_at__day=today.day,
                                       worklog_id =isExist[0]['id'],
                                       worklog_type = 2).exists()):
                         return Response(
                                    {
                                        'error':"you have already clocked out",
                                    },
                                    status = status.HTTP_400_BAD_REQUEST )
                    else:
                        payload['worklog_id'] = isExist[0]['id']
                        payload._mutable = _mutable
                        print('payload of the data 3', payload)
                        serializer = WorkLogDetailsSerilizer( data = payload )
                        if serializer.is_valid():
                            serializer.save()
                            return Response(
                                {'message':"Work log break in successfully",
                                'work_log':isExist[0],
                                'work_log_details': serializer.data},
                                status = status.HTTP_201_CREATED )

                            
                        else:
                            return Response(
                                {'message':serializer.errors},
                                status = status.HTTP_400_BAD_REQUEST
                                )
                elif(int( payload['worklog_type'])== 4):
                    if_pre_obj = WorkLogDetailsSerilizer(
                                        WorkLogsDetailsModel.objects.filter(created_at__year=today.year,
                                       created_at__month=today.month,
                                       created_at__day=today.day,
                                       worklog_id =isExist[0]['id'],
                                       
                                       ).order_by('-created_at').first() ).data
                    if(not if_pre_obj):
                        return Response(
                                    {
                                        'error':"you did not break in yet. ",
                                    },
                                    status = status.HTTP_400_BAD_REQUEST )
                    elif(if_pre_obj and if_pre_obj['worklog_type'] == 4 ):
                        return Response(
                                    {
                                        'error':"you have already break out ",
                                    },
                                    status = status.HTTP_400_BAD_REQUEST )
                    elif (not WorkLogsDetailsModel.objects.filter(created_at__year=today.year,
                                       created_at__month=today.month,
                                       created_at__day=today.day,
                                       worklog_id =isExist[0]['id'],
                                       worklog_type = 3).exists()):
                        return Response(
                                    {
                                        'error':"you have did not break in.",
                                    },
                                    status = status.HTTP_400_BAD_REQUEST )

                    elif(if_pre_obj['worklog_type'] == 3):
                        print(isExist[0]['id'])

                        recent_break_in = WorkLogDetailsSerilizer( WorkLogsDetailsModel.objects.filter(
                                                        worklog_id = isExist[0]['id'],
                                                        work_log_break_id__isnull = False
                                                        ).order_by('-created_at').first()).data
                       
                        previous_break_time = isExist[0]['total_break_time']
                        print('***************', recent_break_in, previous_break_time)
                        total_break_time = datetime.today() - getHours(str(recent_break_in['created_at']))
                        print('***************', total_break_time)

                        total_break_time = datetime.strptime(str(total_break_time),'%H:%M:%S.%f') 
                        total_break_time = math.ceil( math.ceil(total_break_time.second) + 
                                            total_break_time.minute*60 + 
                                            total_break_time.hour*3600)
                       
                        if previous_break_time:
                            # print('previous break time')
                            previous_break_time = datetime.strptime(str(previous_break_time),'%H:%M:%S')

                            previous_break_time = math.ceil( previous_break_time.second + 
                                                    previous_break_time.minute*60 +
                                                    previous_break_time.hour*3600)
                            total_break_time = total_break_time + previous_break_time                 
                        payload['total_break_time'] = str(datetime.time( 
                                                           datetime.strptime(str(dt.timedelta(seconds = total_break_time)) ,'%H:%M:%S') ))
                        payload['worklog_id'] = isExist[0]['id']
                        payload._mutable = _mutable
                        update_worklog = WorkLogSerilizer( WorkLogsModel.objects.get(id = isExist[0]['id']),data = payload)
                        # print(update_worklog)
                        if(update_worklog.is_valid()):
                            update_worklog.save()
                            serializer = WorkLogDetailsSerilizer( data = payload )
                            if serializer.is_valid():
                                serializer.save()
                                return Response(
                                    {'message':"Work log break out successfully",
                                    'work_log':update_worklog.data,
                                    'work_log_details': serializer.data},
                                    status = status.HTTP_201_CREATED )
                        else:
                            return Response(
                                {'message':"Data is not serilized form"},
                                status = status.HTTP_400_BAD_REQUEST
                                )
                else:
                    return Response({'message':'Today data is already exist'},
                                    status=status.HTTP_409_CONFLICT)
        except ValidationError as v:
            print("validation error", v)
class ManageWorkLogs(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            data_worklogs = WorkLogsModel.objects.get(id=pk)
        except (KeyError, WorkLogsModel.DoesNotExist):
            return Response('Data not found', status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = WorkLogSerilizer(data_worklogs)
            return Response({'message':'get the work log',
                             'work_logs' : serializer.data}, 
                                status=status.HTTP_200_OK)

    def put(self, request, pk):

        payload = request.data

        try:
            home = PitStopModel.objects.get(id=pk)
        except (KeyError, PitStopModel.DoesNotExist):

            serializer = PitStopSerializer(data=payload)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:

            serializer = PitStopSerializer(home, data=payload)

            if serializer.is_valid():
                serializer.save()

                parser_classes = (MultiPartParser, FormParser)

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, pk):

    #     try:
    #         home = PitStopModel.objects.get(id=pk)
    #     except (KeyError, PitStopModel.DoesNotExist):
    #         return Response('Data not found', status=status.HTTP_404_NOT_FOUND)
    #     else:
    #         home.delete()
    #         deleteLocation(pk)
    #         return Response('Data deleted', status=status.HTTP_200_OK)
    #     # return Response('Data deleted', status=status.HTTP_200_OK)

class WorkLogsStatus(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            today = datetime.today()
            user_id = getUser(request)

            worklogs = [WorkLogSerilizer(dat).data for dat in WorkLogsModel.objects.filter(
                                       created_at__year=today.year,
                                       created_at__month=today.month,
                                       total_works_hours=None,
                                       user_id = user_id).order_by('-created_at')[:1]]
            if worklogs :  
                time = today - getHours(worklogs[0]['created_at'])
                days, hours, minutes = time.days, time.seconds // 3600, time.seconds // 60 % 60
                if time.days < 1 and hours < 12 :
                    worklog_type = WorkLogsDetailsModel.objects.values('worklog_type').filter(
                                                        worklog_id = worklogs[0]['id'] ).\
                                                        order_by('-created_at')[:1][0]
                    if(int(worklog_type['worklog_type']) ==1):
                        status_log = 3
                    elif(int(worklog_type['worklog_type']) ==3):
                        status_log= 4
                    elif(int(worklog_type['worklog_type']) ==4):
                        status_log= 2
                    else:
                        status_log= 1
                    return Response({'messag':'Work Log status retrieved successfully.',
                                    'status':status_log,
                                    'clock_in' : worklogs[0]['created_at'],
                                    'clock_out' : worklogs[0]['end_at']
                                    },
                                        status=status.HTTP_200_OK)
                else:
                    status_log={
                        'status':1,
                        'clock_in' : None,
                        'clock_out' : None
                    }
                    return Response({'messag':'Work Log status retrieved successfully.',
                                    'status':1,
                                    'clock_in' : None,
                                    'clock_out' : None},
                                        status=status.HTTP_200_OK)
            else:
                status_log={
                    'status':1,
                    'clock_in' : None,
                    'clock_out' : None
                }
                return Response({'messag':'Work Log status retrieved successfully.',
                                'status':1,
                                 'clock_in' : None,
                                 'clock_out' : None},
                                    status=status.HTTP_200_OK)
        except ValidationError as v:
            return Response ({'message':'This is an error is fetching logs',
                                'error':v},
                               status=status.HTTP_400_BAD_REQUEST )

# ******************************* Break logs***********************#
class Notices(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            getAdmin = User.objects.values('admin_id__id').get(id=getUser(request)) 
            print('the admin is here',getAdmin['admin_id__id'])
            notices =  [ NoticesSerializer(dat).data for dat in 
                                NoticesModel.objects.filter(publish=True,admin_id = getAdmin['admin_id__id']) ]
            
            return Response({'messag':'Notices retrieved successfully.',
                            'notices': notices
                            },
                                status=status.HTTP_200_OK)
        except ValidationError as v:
            return Response ({'message':'This is an error is fetching notices',
                                'error':v},
                               status=status.HTTP_400_BAD_REQUEST )

class ManageNotices(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)

    queryset = NoticesModel.objects.all()

    serializer_class = NoticesSerializer

class WorkLogsBreakType(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        user = getUser(request)
        admin_id = User.objects.values('admin_id__id').get(id = user)
        try:

            return Response({'messag':'Break type retieve successfully.',
                            'work_log_breaks':
                            [ WorkLogsBreakSerilizer(dat).data for dat in 
                                WorkLogsBreakModel.objects.filter(admin_id = admin_id['admin_id__id']) ]},
                                status=status.HTTP_200_OK)
        except ValidationError as v:
            return Response ({'message':'This is an error is fetching break',
                                'error':v},
                               status=status.HTTP_400_BAD_REQUEST )

class Styling(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            user = getUser(request)
            print('this is the user', user)
            get_admin = User.objects.values('admin_id__id').get(id = user)

            return Response({'messag':'styling has retieve successfully.',
                            'style':
                            [ StyleSerializer(dat).data for dat in 
                                StyleModel.objects.filter(admin_id = get_admin['admin_id__id']) ][0]},
                                status=status.HTTP_200_OK)
        except ValidationError as v:
            return Response ({'message':'This is an error is fetching break',
                                'error':v},
                               status=status.HTTP_400_BAD_REQUEST )

class Typography(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            user = getUser(request)
            print('this is the user', user)
            get_admin = User.objects.values('admin_id__id').get(id = user)

            return Response({'messag':'styling has retieve successfully.',
                            'typography':
                            [ TypographySerializer(dat).data for dat in 
                                TypographyModel.objects.filter(admin_id = get_admin['admin_id__id']) ][0]},
                                status=status.HTTP_200_OK)
        except ValidationError as v:
            return Response ({'message':'This is an error is fetching break',
                                'error':v},
                               status=status.HTTP_400_BAD_REQUEST )

class StylingTypography(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            user = getUser(request)
            get_admin = User.objects.values('admin_id__id').get(id = user)

            return Response({'messag':'styling has retieve successfully.',
                            'style':
                               StyleSerializer(StyleModel.objects.filter(admin_id = get_admin['admin_id__id']).last()).data,
                            'typography':
                            TypographySerializer(TypographyModel.objects.filter(admin_id = get_admin['admin_id__id']).last()).data},
                                status=status.HTTP_200_OK)
        except ValidationError as v:
            return Response ({'message':'This is an error is fetching break',
                                'error':v},
                               status=status.HTTP_400_BAD_REQUEST )
  
# ****************** get the user from the token**************
def getUser(request):
    token = request.headers.get('Authorization', " ").split(' ')[1]
    decoded_payload = jwt_decode_handler(token)

    return decoded_payload['user_id']

# ************************ formated the date*************
def convert_to_hours(seconds): 
    seconds = seconds % (24 * 3600) 
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
      
    return "%d:%02d:%02d" % (hour, minutes, seconds) 
def getHours(hours):
    date = [hours]
    df = pd.DataFrame(date, columns = ['Date']) 
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%m/%d/%Y %H:%M:%S.%f')
    date = datetime.strptime(df['Date'][0],'%m/%d/%Y %H:%M:%S.%f')
    return date

def base64_file(data, name=None):
    _format, _img_str = data.split(';base64,')
    _name, ext = _format.split('/')
    if not name:
        name = _name.split(":")[-1]
    return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext))

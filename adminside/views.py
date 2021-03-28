from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import  IsAdminUser
from rest_framework import status, generics
from django.db.models import (Sum, 
                            Count, 
                            Avg, 
                            Q)
from django.db.models.functions import (TruncDay,
                                        TruncDate)

from django.http import HttpResponse
from django.conf import settings
from operator import itemgetter
import os
from django.utils.timezone import datetime #important if using timezones
from django.core.exceptions import ValidationError
from django.utils import timezone
import pandas as pd
# jwt decoder
from rest_framework_jwt.utils import jwt_decode_handler
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
from django.core.files.storage import FileSystemStorage

# import serilizers
from .serializer import CustomTokenObtainPairSerializer
# import models
from UserAuth.models import User
from .models import (WorkLogsModel, 
                             WorkLogsDetailsModel,
                             WorkLogsBreakModel,
                             NoticesModel,
                             StyleModel,
                             TypographyModel,
                             RegisterEmailModel,
                             SuspensionEmailModel,
                             AdminEmailModel
                             )

from .serializer import (WorkLogSerilizer, 
                                 WorkLogDetailsSerilizer,
                                 WorkLogsBreakSerilizer,
                                 NoticesSerializer,
                                 StyleSerializer,
                                 TypographySerializer,
                                 RegisterEmailSerializer,
                                 SuspensionEmailSerializer,
                                 AdminEmailSerializer
                                 )

from user.views import getUser

class FrontendAppView(APIView):
    """
    Serves the compiled frontend entry point (only works if you have run `yarn
    run build`).
    """

    def get(self, request):
        try:
            with open(os.path.join(settings.REACT_APP_DIR, 'build', 'index.html')) as f:
                return HttpResponse(f.read())
        except FileNotFoundError:
            # logging.exception('Production build of app not found')
            return HttpResponse(
                """
                    This URL is only used when you have built the production
                    version of the app. Visit http://localhost:3000/ instead, or
                    run `yarn run build` to test the production version.
                    """,
                status=501,
            )

class Notices(APIView):
    permission_classes = (IsAdminUser,)
    def get(self, request):
        try:

            return Response({'messag':'Work Log list retrieved successfully.',
                            'notices':
                            [ NoticesSerializer(dat).data for dat in 
                                NoticesModel.objects.filter(admin_id = getUser(request)) ]},
                                status=status.HTTP_200_OK)
        except ValidationError as v:
            return Response ({'message':'This is an error is fetching notices',
                                'error':v},
                               status=status.HTTP_400_BAD_REQUEST )
    def post(self, request):
        payload = request.data
        # print('notice data', payload)
        # return Response({'data':payload})

        try:
            _mutable = payload._mutable
            payload._mutable = True
            payload['admin_id'] = getUser(request)
            
            payload._mutable = _mutable
            searilizer = NoticesSerializer(data = payload)
            if searilizer.is_valid():
                searilizer.save()
                # print(searilizer.data)
            
                return Response({'message':'Notice has been added', 
                              'data':searilizer.data},
                                status=status.HTTP_201_CREATED)
            else:
                return Response({'message':'Notice has not been added', 
                              'data':searilizer.errors},
                                status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as v:
            return Response({'message':'error occur', 
                                'error':v},
                                    status=status.HTTP_400_BAD_REQUEST)

class ManageNotices(APIView):
    # permission_classes = (IsAdminUser,)

    def get(self, request):
        try:
            data_worklogs = NoticesModel.objects.get(id=pk)
        except (KeyError, WorkLogsModel.DoesNotExist):
            return Response('Data not found', status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = NoticesSerializer(data_worklogs)
            return Response({'message':'get the work log',
                             'work_logs' : serializer.data}, 
                                status=status.HTTP_200_OK)

    def put(self, request, pk):

        payload = request.data

        today = datetime.today()
        _mutable = payload._mutable
        payload._mutable = True
        # print('this is updating', payload)
        payload['updated_at'] = today
        payload._mutable = _mutable
        try:
            home = NoticesModel.objects.get(id=pk)
        except (KeyError, NoticesModel.DoesNotExist):
            serializer = NoticesSerializer(home, data=payload)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = NoticesSerializer(home, data=payload)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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

class WorkLogsBreakType(generics.ListCreateAPIView):
    permission_classes = (IsAdminUser,)
    def get(self, request):
        try:

            return Response({'messag':'Break type retieve successfully.',
                            'notices':
                            [ WorkLogsBreakSerilizer(dat).data for dat in 
                                WorkLogsBreakModel.objects.filter(admin_id = getUser(request)) ]},
                                status=status.HTTP_200_OK)
        except ValidationError as v:
            return Response ({'message':'This is an error is fetching break',
                                'error':v},
                               status=status.HTTP_400_BAD_REQUEST )
    def post(self, request):
        payload = request.data
        try:
            _mutable = payload._mutable
            payload._mutable = True
            payload['admin_id'] = getUser(request)
            
            payload._mutable = _mutable
            searilizer = WorkLogsBreakSerilizer(data = payload)
            if searilizer.is_valid():
                searilizer.save()            
                return Response({'message':'Break has been added', 
                                'data':searilizer.data},
                                    status=status.HTTP_201_CREATED)
            else:
                return Response({'message':'error occur', 
                                'error':searilizer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as v:
            return Response({'message':'error occur', 
                                'error':v},
                                    status=status.HTTP_400_BAD_REQUEST)

class ManageWorkLogsBreakType(generics.UpdateAPIView):
    permission_classes = (IsAdminUser,)

    queryset = WorkLogsBreakModel.objects.all()

    serializer_class = WorkLogsBreakSerilizer

class Styling(generics.ListCreateAPIView):
    permission_classes = (IsAdminUser,)
    def get(self, request):
        try:

            return Response({'messag':'styling has retieve successfully.',
                            'style':
                            [ StyleSerializer(dat).data for dat in 
                                StyleModel.objects.filter(admin_id = getUser(request)) ]},
                                status=status.HTTP_200_OK)
        except ValidationError as v:
            return Response ({'message':'This is an error is fetching break',
                                'error':v},
                               status=status.HTTP_400_BAD_REQUEST )
    def post(self, request):
        payload = request.data
        try:
            _mutable = payload._mutable
            payload._mutable = True
            payload['admin_id'] = getUser(request)
            
            payload._mutable = _mutable
            searilizer = StyleSerializer(data = payload)
            if searilizer.is_valid():
                searilizer.save()
                # print(searilizer.data)
            
                return Response({'message':'style has been added', 
                                'style':searilizer.data},
                                    status=status.HTTP_201_CREATED)
            else:
                return Response({'message':'error occur', 
                                'error':searilizer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as v:
            return Response({'message':'error occur', 
                                'error':v},
                                    status=status.HTTP_400_BAD_REQUEST)

class ManageStyling(generics.UpdateAPIView):
    permission_classes = (IsAdminUser,)

    queryset = StyleModel.objects.all()

    serializer_class = StyleSerializer

class Typography(generics.ListCreateAPIView):
    permission_classes = (IsAdminUser,)
    def get(self, request):
        try:

            return Response({'messag':'styling has retieve successfully.',
                            'typography':
                            [ TypographySerializer(dat).data for dat in 
                                TypographyModel.objects.filter(admin_id = getUser(request)) ]},
                                status=status.HTTP_200_OK)
        except ValidationError as v:
            return Response ({'message':'This is an error is fetching break',
                                'error':v},
                               status=status.HTTP_400_BAD_REQUEST )
    def post(self, request):
        payload = request.data
        print(payload)
        try:
            payload['admin_id'] = getUser(request)
            searilizer = TypographySerializer(data = payload)
            if searilizer.is_valid():
                searilizer.save()
                return Response({'message':'typography has been added', 
                                'typography':searilizer.data},
                                    status=status.HTTP_201_CREATED)
            else:
                return Response({'message':'data is not in serilized form', 
                                'error':searilizer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as v:
            return Response({'message':'error occur', 
                                'error':v},
                                    status=status.HTTP_400_BAD_REQUEST)

class ManageTypography(APIView):
    permission_classes = (IsAdminUser,)

    def put(self, request, pk):
        payload = request.data
        today = datetime.today()
        payload['updated_at'] = today
        try:
            entry = TypographyModel.objects.get(id=pk)
        except (KeyError, TypographyModel.DoesNotExist):
            serializer = TypographySerializer(home, data=payload)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = TypographySerializer(entry, data=payload)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterEmail(generics.ListCreateAPIView):
    permission_classes = (IsAdminUser,)
    def get(self, request):
        try:

            return Response({'messag':'register email data has retieve successfully.',
                            'register_email':
                            [ RegisterEmailSerializer(dat).data for dat in 
                                RegisterEmailModel.objects.filter(admin_id = getUser(request)) ]},
                                status=status.HTTP_200_OK)
        except ValidationError as v:
            return Response ({'message':'This is an error is fetching register email',
                                'error':v},
                               status=status.HTTP_400_BAD_REQUEST )
    def post(self, request):
        payload = request.data
        try:
            payload['admin_id'] = getUser(request)
            searilizer = RegisterEmailSerializer(data = payload)
            if searilizer.is_valid():
                searilizer.save()
                return Response({'message':'email regirstration has been added', 
                                'register_email':searilizer.data},
                                    status=status.HTTP_201_CREATED)
            else:
                return Response({'message':'data is not in serilized form', 
                                'error':searilizer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as v:
            return Response({'message':'error occur', 
                                'error':v},
                                    status=status.HTTP_400_BAD_REQUEST)

class ManageRegisterEmail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAdminUser,)

    queryset = RegisterEmailModel.objects.all()

    serializer_class = RegisterEmailSerializer

class SuspendEmail(generics.ListCreateAPIView):
    permission_classes = (IsAdminUser,)
    def get(self, request):
        try:

            return Response({'messag':'suspend has retieve successfully.',
                            'suspend_email':
                            [ SuspensionEmailSerializer(dat).data for dat in 
                                SuspensionEmailModel.objects.filter(admin_id = getUser(request)) ]},
                                status=status.HTTP_200_OK)
        except ValidationError as v:
            return Response ({'message':'This is an error is fetching break',
                                'error':v},
                               status=status.HTTP_400_BAD_REQUEST )
    def post(self, request):
        payload = request.data
        try:
            payload['admin_id'] = getUser(request)
            searilizer = SuspensionEmailSerializer(data = payload)
            if searilizer.is_valid():
                searilizer.save()
                return Response({'message':'suspend email has been added', 
                                'suspend_email':searilizer.data},
                                    status=status.HTTP_201_CREATED)
            else:
                return Response({'message':'data is not in serilized form', 
                                'error':searilizer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as v:
            return Response({'message':'error occur', 
                                'error':v},
                                    status=status.HTTP_400_BAD_REQUEST)

class ManageSuspendEmail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAdminUser,)

    queryset = SuspensionEmailModel.objects.all()

    serializer_class = SuspensionEmailSerializer

class CkeditorImage(generics.ListCreateAPIView):

    def post(self, request):
        # print(request.build_absolute_uri('/')[:-1] )
        try:
            myfile = request.FILES['upload']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
           
            return Response({"uploaded":1,"url":request.build_absolute_uri('/')[:-1]+uploaded_file_url },
                            status=status.HTTP_200_OK)

        except ValidationError as v:
            return Response({'message':'error occur', 
                                'error':v},
                                    status=status.HTTP_400_BAD_REQUEST)

class AdminEmail(generics.ListCreateAPIView):
    permission_classes = (IsAdminUser,)
    def get(self, request):
        try:

            return Response({'messag':'admin email has retieve successfully.',
                            'admin_email':
                            [ AdminEmailSerializer(dat).data for dat in 
                                AdminEmailModel.objects.filter(admin_id = getUser(request)) ]},
                                status=status.HTTP_200_OK)
        except ValidationError as v:
            return Response ({'message':'This is an error is fetching break',
                                'error':v},
                               status=status.HTTP_400_BAD_REQUEST )
    def post(self, request):
        payload = request.data
        try:
            payload['admin_id'] = getUser(request)
            searilizer = AdminEmailSerializer(data = payload)
            if searilizer.is_valid():
                searilizer.save()
                return Response({'message':'admin email has been added', 
                                'admin_email':searilizer.data},
                                    status=status.HTTP_201_CREATED)
            else:
                return Response({'message':'data is not in serilized form', 
                                'error':searilizer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as v:
            return Response({'message':'error occur', 
                                'error':v},
                                    status=status.HTTP_400_BAD_REQUEST)

class ManageAdminEmail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAdminUser,)

    queryset = AdminEmailModel.objects.all()

    serializer_class = AdminEmailSerializer

class DashboardAnalytics(APIView):
    permission_classes = (IsAdminUser,)
    
    def get(self, request):
        print('this is inside the user', )
        try:
            today = datetime.today()

            data = {}
            user = getUser(request)
            # total = Count('total_user', filter=Q(book__rating__gt=5))
            # active = Count('book', filter=Q(book__rating__gt=5))
            # not_active = Count('book', filter=Q(book__rating__gt=5))
            # all_user = User.objects.filter(admin_id = getUser(request) ).\
            #         aggregate(Count('id'))
            # active_user = User.objects.filter(admin_id = getUser(request), is_active = True ).\
            #         aggregate(Count('is_active'))
            data['all_user'] = User.objects.filter(admin_id = user ).\
                    aggregate(Count('id'))['id__count']
            data['active_user'] = User.objects.filter(admin_id = user, is_active = True ).\
                    aggregate(Count('is_active'))['is_active__count']
            data['inactive_user'] = abs(data['all_user'] - data['active_user'])
            data['register_records'] = WorkLogsModel.objects.filter(user_id__admin_id = user).\
                                        aggregate(Count('id'))['id__count']
            data['monthly_data'] = WorkLogsModel.objects.filter(user_id__admin_id = user, 
                                        created_at__month = today.month ).\
                                        aggregate(Count('id'))['id__count']
            data['graph_data'] = WorkLogsModel.objects.filter(user_id__admin_id = user, 
                                        created_at__month = today.month ).\
                                        annotate(date = TruncDate('created_at'))\
                                        .order_by('date')\
                                        .values("date")\
                                        .annotate(**{'total':Count('created_at')})\
                                      
        except ValidationError as v:
            return Response({'message':'there is an error',
                            
                            'error' : v},
                            status= status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'message':'analytics data',
                            'analytics': data })

